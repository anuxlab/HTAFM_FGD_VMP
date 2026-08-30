import (
	"k8s.io/kubernetes/pkg/scheduler/framework"
	"k8s.io/kubernetes/pkg/scheduler/framework/runtime"
	"https://github.com/anuxlab/HTAFM_FGD_VMP/custom-scheduler/htafm" // adjust import path
)

func init() {
	// Register HTAFMScore plugin
	registry := runtime.NewRegistry()
	registry.Register(htafm.Name,
		func(configuration runtime.Unknown, f framework.Handle) (framework.Plugin, error) {
			// parse configuration for variant
			var args struct {
				Variant string `json:"variant"`
			}
			// You need to parse the configuration into args.
			// This is pseudo; you'd use the runtime.DecodeInto.
			// For simplicity, we'll just return the default.
			return htafm.New(nil, f, "cut")
		})
}