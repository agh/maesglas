package main

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/derailed/k9s/internal/config"
)

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintln(os.Stderr, "expected one skin file")
		os.Exit(2)
	}
	styles := config.NewStyles()
	if err := styles.Load(os.Args[1], false); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	if err := json.NewEncoder(os.Stdout).Encode(styles); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
