set background=light
highlight clear
if exists('syntax_on')
  syntax reset
endif
set termguicolors
let g:colors_name = 'maesglas-chalk'
highlight Normal guifg=#14231E guibg=#F1F5F0 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight NormalNC guifg=#14231E guibg=#F1F5F0 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight Comment guifg=#404D44 guibg=#F1F5F0 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight LineNr guifg=#47514A guibg=#F1F5F0 gui=NONE ctermfg=8 ctermbg=NONE cterm=NONE
highlight CursorLineNr guifg=#14231E guibg=#E9F0E9 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight CursorLine guifg=#14231E guibg=#E9F0E9 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight Statement guifg=#654C75 guibg=#F1F5F0 gui=NONE ctermfg=13 ctermbg=NONE cterm=NONE
highlight PreProc guifg=#654C75 guibg=#F1F5F0 gui=NONE ctermfg=13 ctermbg=NONE cterm=NONE
highlight Identifier guifg=#14231E guibg=#F1F5F0 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight Constant guifg=#795A2A guibg=#F1F5F0 gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
highlight Number guifg=#795A2A guibg=#F1F5F0 gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
highlight String guifg=#38573C guibg=#F1F5F0 gui=NONE ctermfg=10 ctermbg=NONE cterm=NONE
highlight Character guifg=#38573C guibg=#F1F5F0 gui=NONE ctermfg=10 ctermbg=NONE cterm=NONE
highlight Operator guifg=#14231E guibg=#F1F5F0 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight SpecialComment guifg=#404D44 guibg=#F1F5F0 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight Underlined guifg=#366F72 guibg=#F1F5F0 gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
highlight Ignore guifg=#404D44 guibg=#F1F5F0 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight Type guifg=#366F72 guibg=#F1F5F0 gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
highlight Function guifg=#2D475A guibg=#F1F5F0 gui=NONE ctermfg=12 ctermbg=NONE cterm=NONE
highlight Special guifg=#366F72 guibg=#F1F5F0 gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
highlight Delimiter guifg=#14231E guibg=#F1F5F0 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight NonText guifg=#47514A guibg=#F1F5F0 gui=NONE ctermfg=8 ctermbg=NONE cterm=NONE
highlight SpecialKey guifg=#47514A guibg=#F1F5F0 gui=NONE ctermfg=8 ctermbg=NONE cterm=NONE
highlight Folded guifg=#404D44 guibg=#E9F0E9 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight FoldColumn guifg=#47514A guibg=#F1F5F0 gui=NONE ctermfg=8 ctermbg=NONE cterm=NONE
highlight SignColumn guifg=#14231E guibg=#F1F5F0 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight Visual guifg=#14231E guibg=#D9EBE2 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight Search guifg=#14231E guibg=#F4ECD8 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight IncSearch guifg=#14231E guibg=#F0E6CD gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight DiffAdd guifg=#14231E guibg=#E6F1E6 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight DiffDelete guifg=#662B24 guibg=#FAE9E5 gui=NONE ctermfg=9 ctermbg=NONE cterm=NONE
highlight DiffChange guifg=#14231E guibg=#F3EDDC gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight DiffText guifg=#14231E guibg=#DCEBDC gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight StatusLine guifg=#654C75 guibg=#E9F0E9 gui=NONE ctermfg=13 ctermbg=NONE cterm=NONE
highlight StatusLineNC guifg=#404D44 guibg=#E9F0E9 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight VertSplit guifg=#53655E guibg=#F1F5F0 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight Pmenu guifg=#14231E guibg=#E9F0E9 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight PmenuSel guifg=#14231E guibg=#D9EBE2 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight PmenuSbar guifg=#53655E guibg=#E9F0E9 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight PmenuThumb guifg=#14231E guibg=#E9F0E9 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight Error guifg=#662B24 guibg=#F1F5F0 gui=NONE ctermfg=9 ctermbg=NONE cterm=NONE
highlight ErrorMsg guifg=#662B24 guibg=#F1F5F0 gui=NONE ctermfg=9 ctermbg=NONE cterm=NONE
highlight WarningMsg guifg=#795A2A guibg=#F1F5F0 gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
highlight Todo guifg=#795A2A guibg=#F1F5F0 gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
highlight Title guifg=#14231E guibg=#F1F5F0 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight Directory guifg=#2D475A guibg=#F1F5F0 gui=NONE ctermfg=12 ctermbg=NONE cterm=NONE
highlight MatchParen guifg=#14231E guibg=#F0E6CD gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight TabLine guifg=#404D44 guibg=#E9F0E9 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight TabLineSel guifg=#14231E guibg=#D9EBE2 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight TabLineFill guifg=#404D44 guibg=#E9F0E9 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight Conceal guifg=#404D44 guibg=#F1F5F0 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight CursorColumn guifg=#14231E guibg=#E9F0E9 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight ColorColumn guifg=#14231E guibg=#E9F0E9 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight CursorLineSign guifg=#14231E guibg=#E9F0E9 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight CursorLineFold guifg=#404D44 guibg=#E9F0E9 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight LineNrAbove guifg=#47514A guibg=#F1F5F0 gui=NONE ctermfg=8 ctermbg=NONE cterm=NONE
highlight LineNrBelow guifg=#47514A guibg=#F1F5F0 gui=NONE ctermfg=8 ctermbg=NONE cterm=NONE
highlight MoreMsg guifg=#38573C guibg=#F1F5F0 gui=NONE ctermfg=10 ctermbg=NONE cterm=NONE
highlight ModeMsg guifg=#14231E guibg=#F1F5F0 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight Question guifg=#366F72 guibg=#F1F5F0 gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
highlight QuickFixLine guifg=#14231E guibg=#D9EBE2 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight StatusLineTerm guifg=#654C75 guibg=#E9F0E9 gui=NONE ctermfg=13 ctermbg=NONE cterm=NONE
highlight StatusLineTermNC guifg=#404D44 guibg=#E9F0E9 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight VisualNOS guifg=#14231E guibg=#D9EBE2 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight WildMenu guifg=#14231E guibg=#D9EBE2 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight ToolbarLine guifg=#14231E guibg=#E9F0E9 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight ToolbarButton guifg=#14231E guibg=#D9EBE2 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight PmenuMatch guifg=#366F72 guibg=#E9F0E9 gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
highlight PmenuMatchSel guifg=#366F72 guibg=#D9EBE2 gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
highlight PmenuKind guifg=#404D44 guibg=#E9F0E9 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight PmenuKindSel guifg=#404D44 guibg=#D9EBE2 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight PmenuExtra guifg=#404D44 guibg=#E9F0E9 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight PmenuExtraSel guifg=#404D44 guibg=#D9EBE2 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
highlight CurSearch guifg=#14231E guibg=#F0E6CD gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
highlight SpellBad guifg=#14231E guibg=#F1F5F0 guisp=#662B24 gui=undercurl cterm=underline
highlight SpellCap guifg=#14231E guibg=#F1F5F0 guisp=#795A2A gui=undercurl cterm=underline
highlight SpellRare guifg=#14231E guibg=#F1F5F0 guisp=#366F72 gui=undercurl cterm=underline
highlight SpellLocal guifg=#14231E guibg=#F1F5F0 guisp=#366F72 gui=undercurl cterm=underline
