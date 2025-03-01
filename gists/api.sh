#!/bin/bash

banner() {
  echo "sunosh - a suno custom cli with gpt integration for fast song generation"
  echo "by Colin J.Brigato <colin@brigato.fr>"
  echo '-'
}

## CONF
#set it from https://clerk.suno.com/v1/client?_clerk_js_version=4.73.2 request in developer tools
COOKIE=""
#get it from https://platform.openai.com/api-keys
OPENAI_API_KEY=""

# CONST
SUNO_FEED_API="https://studio-api.suno.ai/api/feed/?page=0"
SUNO_CLERK_CLIENT_URL="https://clerk.suno.com/v1/client?_clerk_js_version=4.73.2"
SUNO_GENERATE_API="https://studio-api.suno.ai/api/generate/v2/"
SUNO_TOKEN_API_HEAD="https://clerk.suno.com/v1/client/sessions"
SUNO_TOKEN_API_TAIL="tokens?_clerk_js_version=4.73.2"
OPENAI_COMPLETION_API="https://api.openai.com/v1/chat/completions"

## GLOBAL VAR
SUNO_TOKEN=""
SUNO_SID=""
SONG=""
NSONG=""
GPT_PROMPT=""
SUNO_TAGS=""
SUNO_TITLE=""
SUNO_PROMPT=""

get_suno_cookie() {
  echo "$COOKIE"
}

get_openai_api_key() {
  echo "$OPENAI_API_KEY"
}

get_suno_token() {
  echo "$SUNO_TOKEN"
}

set_suno_token() {
  SUNO_TOKEN="$1"
}

get_suno_sid() {
  __cookie="$(get_suno_cookie)"
  curl -s "$SUNO_CLERK_CLIENT_URL" \
    "${COMMON_HEADER[@]}" \
    -H 'authority: clerk.suno.com' \
    -H "cookie: ${__cookie}" | jq -r '.response.last_active_session_id'
}

make_suno_client_session_url() {
  _cookie="$(get_suno_cookie)"
  _sid="$(get_suno_sid "$_cookie")"
  echo "${SUNO_TOKEN_API_HEAD}/${_sid}/${SUNO_TOKEN_API_TAIL}"
}

refresh_suno_token() {
  __cookie="$(get_suno_cookie)"
  __token_url="$(make_suno_client_session_url)"
  set_suno_token "$(curl -s "$__token_url" -X 'POST' -H 'authority: clerk.suno.com' "${COMMON_HEADER[@]}" -H 'content-length: 0' -H 'content-type: application/x-www-form-urlencoded' -H "cookie: ${__cookie}" \  | jq -r '.jwt')"
}

normalize_json_string() {
  echo "$1" | sed -E ':a;N;$!ba;s/\r{0,1}\n/\\n/g'
}

gpt_json() {
  echo -n '{"messages":[{"role":"system","content":[]},{"role":"user","content":[{"type":"text","text":"'
  echo -n "$1"
  echo -n '"}]}],"temperature":1,"top_p":1,"frequency_penalty":0,"presence_penalty":0,"seed":null,"model":"gpt-3.5-turbo","stream":false}'
}

songwriter() {
  now=$(date +%s)
  file=".sg${now}.txt"
  res=".sg${now}.json"
  prompt="$GPT_PROMPT"
  gpt_json "$prompt. Song  structure mentions should be in english." >$file
  curl -s "$OPENAI_COMPLETION_API" -H 'accept: text/event-stream' -H 'accept-language: fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7' -H "authorization: Bearer $(get_openai_api_key)" -H 'cache-control: no-cache' -H 'content-type: application/json' -H 'dnt: 1' -H 'openai-organization: org-VaYWuIKXWQV7W5OCgWpTb4lT' -H 'origin: https://platform.openai.com' -H 'pragma: no-cache' -H 'priority: u=1, i' -H 'referer: https://platform.openai.com/' -H 'sec-ch-ua: \"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"' -H 'sec-ch-ua-mobile: ?0' -H 'sec-ch-ua-platform: \"Windows\"' -H 'sec-fetch-dest: empty' -H 'sec-fetch-mode: cors' -H 'sec-fetch-site: same-site' -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36' --data-raw "$(cat $file)" >$res
  cat $res | jq -r '.choices[0].message.content'
  rm $res $file
}

normalize_structure_metatags() {
  echo "$1" | sed -r 's/^.?.?[Rr]efrain.?.?$/[chorus]/g' | sed -r 's/^.?.?[Cc]ouplet.?.?.?.?$/[verse]/g' | sed -r 's/^.?.?[Vv]ers.?.?.?.?.?$/[verse]/g' | sed -r 's/^.?.?[Pp]ont.?.?.?.?$/[bridge]/g' | sed -r 's/^.?.?[Ff]in.?.?.?.?$/[outro]/g' | sed -r 's/^.?.?[Bb]ridge.?.?.?.?$/[bridge]/g' | sed -r 's/^.?.?[Cc]horus.?.?.?.?$/[chorus]/g' | sed -r 's/^.?.?[Oo]utro.?.?.?.?$/[outro]/g' | sed -r 's/^.?.?[Tt]itle.?.*$//g' | sed -r 's/^.?.?[Pp]re.[Cc]horus.?.?.?.?$/[pre-chorus]/g'
}

generate_lyrics() {
  echo -n "* Generating song..."
  SONG="$(songwriter "$GPT_PROMPT . Les infos de structure de la chansons doivent etre en anglais")"
  NSONG="$(normalize_structure_metatags "$SONG")"
  echo "[OK]"
  echo "* Checking song has proper structure..."
  if ! grep -qi '\[verse\]' <<<"$NSONG"; then
    echo "  -> song has no proper structure"
    echo "     please look at gpt answer and modify your prompt accordingly"
    echo '---------------------------------'
    echo "$NSONG"
    echo '---------------------------------'
    read_lyrics
    generate_lyrics
    return
  fi
  echo '----------------------------------'
  echo "$NSONG"
  echo '----------------------------------'
  SUNO_SONG="$(normalize_json_string "$NSONG")"
}

validate_song() {
  PS3="Do you want to use this generated lyrics: "
  sopts=("Use it" "Regenerate (same instructions)" "Change instructions" "Abort (quit)")
  select sopt in "${sopts[@]}"; do
    case $sopt in
    "Use it")
      echo "Using generated song"
      break
      ;;
    "Regenerate (same instructions)")
      echo "Regenerating new version with $GPT_PROMPT"
      generate_lyrics
      ;;
    "Change instructions")
      echo "Restarting lyrics instructions..."
      read_lyrics
      generate_lyrics
      ;;
    "Abort (quit)")
      echo "Abort: Quitting"
      exit 121
      ;;
    *) echo "invalid option $REPLY" ;;
    esac
  done
}

COMMON_HEADER=(
  "-H"
  "'accept: */*'"
  "-H"
  "'accept-language: fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'"
  "-H"
  "'cache-control: no-cache'"
  "-H"
  "'dnt: 1'"
  "-H"
  "'origin: https://suno.com'"
  "-H"
  "'pragma: no-cache'"
  "-H"
  "'referer: https://suno.com/'"
  "-H"
  "'sec-ch-ua: "Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"'"
  "-H"
  "'sec-ch-ua-mobile: ?0'"
  "-H"
  "'sec-ch-ua-platform: "Windows"'"
  "-H"
  "'sec-fetch-dest: empty'"
  "-H"
  "'sec-fetch-mode: cors'"
  "-H"
  "'sec-fetch-site: same-site'"
  "-H"
  "'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'"
  "--compressed"
)

# feed [retcode]
feed() {
  __token="$(get_suno_token)"
  if [[ "$1" == "retcode" ]]; then
    curl -s "$SUNO_FEED_API" \
      -H 'authority: studio-api.suno.ai' \
      "${COMMON_HEADER[@]}" \
      -H "authorization: Bearer $__token" \
      --write-out "%{http_code}\n" \
      --output /dev/null
  else
    curl -s "$SUNO_FEED_API" \
      -H 'authority: studio-api.suno.ai' \
      "${COMMON_HEADER[@]}" \
      -H "authorization: Bearer $__token"
  fi
}


# generate_suno_songs "PROMPT" "TAGS" "TITLE"
generate_suno_songs() {

  _token="$(get_suno_token)"
  _prompt="$1"
  _tags="$2"
  _mv="chirp-v3-5"
  _title="$3"
  _postambule="\"mv\":\"${_mv}\",\"continue_clip_id\":null,\"continue_at\":null,\"infill_start_s\":null,\"infill_end_s\":null"

  prompt="\"prompt\":\"${_prompt}\""
  tags="\"tags\":\"${_tags}\""
  title="\"title\":\"${_title}\""
  datas="{${prompt},${tags},${title},${_postambule}}"

  curl -s "$SUNO_GENERATE_API" \
    -H 'authority: studio-api.suno.ai' \
    "${COMMON_HEADER[@]}" \
    -H "authorization: Bearer $_token" \
    --data-raw "$datas" | jq -r .clips[].id
}

get_audio_url() {
  code="$(feed retcode)"
  if grep -q "401" <<<"$code"; then
    refresh_suno_token
  fi
  feed | jq -r ".[]|select(.id | contains(\"${1}\")).audio_url"
}

is_audio_downloadable() {
  get_audio_url "$1" | grep -q "mp3"
}

is_audio_listenable() {
  get_audio_url "$1" | egrep -q "audiopipe|mp3"
}

wait_audio() {

  __uid="$1"
  __t="$2"
  __id="$3"
  __state="$4"

  echo -n "[$__t-$__id.mp3] $__uid Waiting for $__state state..."

  while :; do
    echo -n "."
    if is_audio_${__state} "$__uid"; then
      dl="$(get_audio_url $__uid)"
      echo -n "[OK]"
      echo " -> $dl"
      if [[ $__state == "downloadable" ]]; then
        wget -O "${__t}-${__id}.mp3" "$dl"
      fi
      break
    else
      sleep 5
    fi
  done

}

read_lyrics() {
  echo "Type lyrics instruction in chatGPT way, e.g: écris moi une chanson sur le pain, en francais"
  read -p 'lyrics instructions: ' songwriter_prompt
  if [ -z "$songwriter_prompt" ]; then
    echo "Aborting: lyrics instructions are required"
    exit 122
  fi
  GPT_PROMPT="$songwriter_prompt"
}

read_tags() {
  echo "Type style/genre a.k.a 'tags', comma separated. e.g: edm, pop, electro"
  read -p 'tags: ' suno_tags
  if [ -z "$suno_tags" ]; then
    echo "error: tags are required"
    read_tags
    return
  fi
  SUNO_TAGS="$suno_tags"
}

read_title() {
  echo "Choose any title:"
  read -p 'title: ' suno_title
  if [ -z "$suno_title" ]; then
    echo "error: title is required"
    read_title
    return
  fi
  SUNO_TITLE="$suno_title"
}

#retrieve_suno_songs "<suno_id1> <suno_id2>" "[listenable|downloadable]"
retrieve_suno_songs() {
  idcount=0
  _list="$1"
  _state="$2"

  for I in $_list; do
    wait_audio $I "$SUNO_TITLE" "$idcount" "$_state"
    idcount=$((idcount + 1))
  done
}

echo
echo "I. LYRICS"
echo '---------'
read_lyrics
generate_lyrics
validate_song

echo
echo "II. TAGS"
echo '--------'
read_tags

echo
echo "III. TITLE"
echo '--------'
read_title

echo
echo "V. BLACK MAGIC !"
echo '----------------'

echo "* Generating TOKEN"
refresh_suno_token
echo "* Generating song:"
echo "  -> prompt: $SUNO_SONG"
echo "  -> genres: $SUNO_TAGS"
echo "  -> title: $SUNO_TITLE"
_ids=$(generate_suno_songs "$SUNO_SONG" "$SUNO_TAGS" "$SUNO_TITLE")
echo "* Generated IDS:"
for I in $_ids; do
  echo "  -> $I"
done

echo
echo "VI. BRACING OURSELF"
echo '------------------'
sleep 5

retrieve_suno_songs "$_ids" "listenable"

if [[ "$1" == "--with-download" ]]; then
  echo "* --with-download asked, this could take a while"
  retrieve_suno_songs "$_ids" "downloadable"
fi

echo '----'
echo "DONE"