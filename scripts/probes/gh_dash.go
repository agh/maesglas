package main

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/dlvhdr/gh-dash/v4/internal/config"
	"github.com/dlvhdr/gh-dash/v4/internal/tui/theme"
)

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintln(os.Stderr, "expected one configuration file")
		os.Exit(2)
	}
	cfg, err := config.ParseConfig(config.Location{
		ConfigFlag: os.Args[1], SkipGlobalConfig: true,
	})
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	if cfg.Theme == nil || cfg.Theme.Colors == nil {
		fmt.Fprintln(os.Stderr, "theme colors were not loaded")
		os.Exit(1)
	}
	result := struct {
		Colors config.ColorTheme
		Theme  theme.Theme
	}{cfg.Theme.Colors.Inline, theme.ParseTheme(&cfg)}
	if err := json.NewEncoder(os.Stdout).Encode(result); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
