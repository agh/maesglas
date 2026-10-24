#!/bin/sh
if [ -z "${NO_COLOR+x}" ] && [ "${TERM:-dumb}" != dumb ] && [ -t 1 ]; then
  export FZF_DEFAULT_OPTS="${FZF_DEFAULT_OPTS:-} --color=fg:#F1F6F0,bg:#0D1613,fg+:#F1F6F0,bg+:#212F2A,hl:#C9EDEE,hl+:#C9EDEE,info:#CDD7D0,prompt:#F1F6F0,pointer:#DECCEA,marker:#B2D8B6,spinner:#CDD7D0,header:#CDD7D0,border:#90A49C,label:#F1F6F0,gutter:#0D1613,preview-fg:#F1F6F0,preview-bg:#121D19 --pointer=>"
fi
