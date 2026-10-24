#!/bin/sh
if [ -z "${NO_COLOR+x}" ] && [ "${TERM:-dumb}" != dumb ] && [ -t 1 ]; then
  export FZF_DEFAULT_OPTS="${FZF_DEFAULT_OPTS:-} --color=fg:#14231E,bg:#F1F5F0,fg+:#14231E,bg+:#D9EBE2,hl:#366F72,hl+:#366F72,info:#404D44,prompt:#14231E,pointer:#654C75,marker:#38573C,spinner:#404D44,header:#404D44,border:#53655E,label:#14231E,gutter:#F1F5F0,preview-fg:#14231E,preview-bg:#E9F0E9 --pointer=>"
fi
