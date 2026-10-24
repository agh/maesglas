set background=dark
highlight clear
if exists('syntax_on')
  syntax reset
endif
set termguicolors
let g:colors_name = 'maesglas-shale'
highlight Normal guifg=#F1F6F0 guibg=#0D1613 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight NormalNC guifg=#F1F6F0 guibg=#0D1613 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight Comment guifg=#CDD7D0 guibg=#0D1613 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight LineNr guifg=#C8D3CB guibg=#0D1613 gui=NONE ctermfg=8 ctermbg=NONE cterm=NONE
highlight CursorLineNr guifg=#F1F6F0 guibg=#121D19 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight CursorLine guifg=#F1F6F0 guibg=#121D19 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight Statement guifg=#DECCEA guibg=#0D1613 gui=NONE ctermfg=13 ctermbg=NONE cterm=NONE
highlight PreProc guifg=#DECCEA guibg=#0D1613 gui=NONE ctermfg=13 ctermbg=NONE cterm=NONE
highlight Identifier guifg=#F1F6F0 guibg=#0D1613 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight Constant guifg=#FBDCB2 guibg=#0D1613 gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
highlight Number guifg=#FBDCB2 guibg=#0D1613 gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
highlight String guifg=#B2D8B6 guibg=#0D1613 gui=NONE ctermfg=10 ctermbg=NONE cterm=NONE
highlight Character guifg=#B2D8B6 guibg=#0D1613 gui=NONE ctermfg=10 ctermbg=NONE cterm=NONE
highlight Operator guifg=#F1F6F0 guibg=#0D1613 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight SpecialComment guifg=#CDD7D0 guibg=#0D1613 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight Underlined guifg=#C9EDEE guibg=#0D1613 gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
highlight Ignore guifg=#CDD7D0 guibg=#0D1613 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight Type guifg=#C9EDEE guibg=#0D1613 gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
highlight Function guifg=#9FBDD5 guibg=#0D1613 gui=NONE ctermfg=12 ctermbg=NONE cterm=NONE
highlight Special guifg=#C9EDEE guibg=#0D1613 gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
highlight Delimiter guifg=#F1F6F0 guibg=#0D1613 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight NonText guifg=#C8D3CB guibg=#0D1613 gui=NONE ctermfg=8 ctermbg=NONE cterm=NONE
highlight SpecialKey guifg=#C8D3CB guibg=#0D1613 gui=NONE ctermfg=8 ctermbg=NONE cterm=NONE
highlight Folded guifg=#CDD7D0 guibg=#121D19 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight FoldColumn guifg=#C8D3CB guibg=#0D1613 gui=NONE ctermfg=8 ctermbg=NONE cterm=NONE
highlight SignColumn guifg=#F1F6F0 guibg=#0D1613 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight Visual guifg=#F1F6F0 guibg=#212F2A gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight Search guifg=#F1F6F0 guibg=#262114 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight IncSearch guifg=#F1F6F0 guibg=#312B1C gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight DiffAdd guifg=#F1F6F0 guibg=#1B241B gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight DiffDelete guifg=#E99E92 guibg=#2B1E1B gui=NONE ctermfg=9 ctermbg=NONE cterm=NONE
highlight DiffChange guifg=#F1F6F0 guibg=#252116 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight DiffText guifg=#F1F6F0 guibg=#232F23 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight StatusLine guifg=#DECCEA guibg=#121D19 gui=NONE ctermfg=13 ctermbg=NONE cterm=NONE
highlight StatusLineNC guifg=#CDD7D0 guibg=#121D19 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight VertSplit guifg=#90A49C guibg=#0D1613 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight Pmenu guifg=#F1F6F0 guibg=#121D19 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight PmenuSel guifg=#F1F6F0 guibg=#212F2A gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight PmenuSbar guifg=#90A49C guibg=#121D19 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight PmenuThumb guifg=#F1F6F0 guibg=#121D19 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight Error guifg=#E99E92 guibg=#0D1613 gui=NONE ctermfg=9 ctermbg=NONE cterm=NONE
highlight ErrorMsg guifg=#E99E92 guibg=#0D1613 gui=NONE ctermfg=9 ctermbg=NONE cterm=NONE
highlight WarningMsg guifg=#FBDCB2 guibg=#0D1613 gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
highlight Todo guifg=#FBDCB2 guibg=#0D1613 gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
highlight Title guifg=#F1F6F0 guibg=#0D1613 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight Directory guifg=#9FBDD5 guibg=#0D1613 gui=NONE ctermfg=12 ctermbg=NONE cterm=NONE
highlight MatchParen guifg=#F1F6F0 guibg=#312B1C gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight TabLine guifg=#CDD7D0 guibg=#121D19 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight TabLineSel guifg=#F1F6F0 guibg=#212F2A gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight TabLineFill guifg=#CDD7D0 guibg=#121D19 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight Conceal guifg=#CDD7D0 guibg=#0D1613 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight CursorColumn guifg=#F1F6F0 guibg=#121D19 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight ColorColumn guifg=#F1F6F0 guibg=#121D19 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight CursorLineSign guifg=#F1F6F0 guibg=#121D19 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight CursorLineFold guifg=#CDD7D0 guibg=#121D19 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight LineNrAbove guifg=#C8D3CB guibg=#0D1613 gui=NONE ctermfg=8 ctermbg=NONE cterm=NONE
highlight LineNrBelow guifg=#C8D3CB guibg=#0D1613 gui=NONE ctermfg=8 ctermbg=NONE cterm=NONE
highlight MoreMsg guifg=#B2D8B6 guibg=#0D1613 gui=NONE ctermfg=10 ctermbg=NONE cterm=NONE
highlight ModeMsg guifg=#F1F6F0 guibg=#0D1613 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight Question guifg=#C9EDEE guibg=#0D1613 gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
highlight QuickFixLine guifg=#F1F6F0 guibg=#212F2A gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight StatusLineTerm guifg=#DECCEA guibg=#121D19 gui=NONE ctermfg=13 ctermbg=NONE cterm=NONE
highlight StatusLineTermNC guifg=#CDD7D0 guibg=#121D19 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight VisualNOS guifg=#F1F6F0 guibg=#212F2A gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight WildMenu guifg=#F1F6F0 guibg=#212F2A gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight ToolbarLine guifg=#F1F6F0 guibg=#121D19 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight ToolbarButton guifg=#F1F6F0 guibg=#212F2A gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight PmenuMatch guifg=#C9EDEE guibg=#121D19 gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
highlight PmenuMatchSel guifg=#C9EDEE guibg=#212F2A gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
highlight PmenuKind guifg=#CDD7D0 guibg=#121D19 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight PmenuKindSel guifg=#CDD7D0 guibg=#212F2A gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight PmenuExtra guifg=#CDD7D0 guibg=#121D19 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight PmenuExtraSel guifg=#CDD7D0 guibg=#212F2A gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight CurSearch guifg=#F1F6F0 guibg=#312B1C gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight SpellBad guifg=#F1F6F0 guibg=#0D1613 guisp=#E99E92 gui=undercurl cterm=underline
highlight SpellCap guifg=#F1F6F0 guibg=#0D1613 guisp=#FBDCB2 gui=undercurl cterm=underline
highlight SpellRare guifg=#F1F6F0 guibg=#0D1613 guisp=#C9EDEE gui=undercurl cterm=underline
highlight SpellLocal guifg=#F1F6F0 guibg=#0D1613 guisp=#C9EDEE gui=undercurl cterm=underline
