import yt_dlp

url = 'https://www.ted.com/talks/kathryn_valentine_what_successful_negotiators_do_differently'

ydl_opts = {
    'quiet': True,
    'no_warnings': True,
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        print('Title:', info.get('title'))
        for fmt in info.get('formats', [])[:3]:
            print('Format:', fmt.get('format_id'), fmt.get('ext'), fmt.get('url', 'N/A')[:80])
        direct_url = info.get('url')
        if direct_url:
            print('Direct URL found!')
        else:
            print('No direct URL')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
