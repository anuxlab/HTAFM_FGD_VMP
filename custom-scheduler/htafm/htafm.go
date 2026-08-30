package htafm

import (
	"context"

	"k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/kubernetes/pkg/scheduler/framework"
)

const (
	Name = "HTAFMScore"
)

type HTAFM struct {
	handle  framework.Handle
	variant string // "cut", "entropy", "hier"
	hg      *Hypergraph
}

var _ framework.ScorePlugin = &HTAFM{}

// New initializes the plugin.
func New(obj runtime.Object, h framework.Handle, variant string) (framework.Plugin, error) {
	return &HTAFM{
		handle:  h,
		variant: variant,
	}, nil
}

func (pl *HTAFM) Name() string {
	return Name
}

// Score calculates the fragmentation score for a node.
// Lower score is better.
func (pl *HTAFM) Score(ctx context.Context, state *framework.CycleState, pod *v1.Pod, nodeName string) (int64, *framework.Status) {
	// Get the node object
	nodeInfo, err := pl.handle.SnapshotSharedLister().NodeInfos().Get(nodeName)
	if err != nil {
		return 0, framework.NewStatus(framework.Error, "failed to get node info")
	}
	node := nodeInfo.Node()

	// Build hypergraph if not already built.
	// In production, we would build it once and update it as cluster changes.
	// For simplicity, we rebuild on each score (inefficient but works for PoC).
	// To optimize, we can cache the hypergraph and update on node changes.
	allNodes, _ := pl.handle.SnapshotSharedLister().NodeInfos().List()
	nodes := make([]*v1.Node, 0, len(allNodes))
	for _, ni := range allNodes {
		nodes = append(nodes, ni.Node())
	}
	pl.hg = NewHypergraph(nodes)

	// Compute TAFI for the whole cluster if we were to place on this node (simulate)
	// But we need to consider the current placement; we can compute TAFI after hypothetical placement.
	// For simplicity, we compute the current TAFI and use it as a score.
	// A more precise approach would calculate the delta.
	// We'll treat the current fragmentation as the score.
	tafi := ComputeTAFI(pl.hg, nodes, pl.variant)

	// Scale to int64 (0-100)
	score := int64(tafi * 100)
	if score > 100 {
		score = 100
	}
	return 100 - score, framework.NewStatus(framework.Success, "") // invert so lower fragmentation = higher score
}

func (pl *HTAFM) ScoreExtensions() framework.ScoreExtensions {
	return nil // we don't need NormalizeScore
}