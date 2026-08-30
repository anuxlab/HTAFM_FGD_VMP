package htafm

import (
	"k8s.io/kubernetes/pkg/scheduler/framework/runtime"
)

func init() {
	// Register the plugin with the runtime registry.
	// The framework will call New() with the appropriate config.
	runtime.Register(Name, New)
}