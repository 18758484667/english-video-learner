import yt_dlp

url = 'https://www.ted.com/talks/kathryn_valentine_what_successful_negotiators_do_differently'

with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
    info = ydl.extract_info(url, download=False)
    for i, fmt in enumerate(info.get('formats', [])):
        fid = fmt.get('format_id', '')
        furl = fmt.get('url', '')
        vcodec = fmt.get('vcodec', 'none')
        acodec = fmt.get('acodec', 'none')
        height = fmt.get('height', 0) or 0
        if 'audio' in fid.lower() or 'a1' in fid.lower():
            print(f'AUDIO: {fid} | acodec={acodec} | height={height}')
        elif vcodec != 'none':
            print(f'VIDEO: {fid} | height={height}')
