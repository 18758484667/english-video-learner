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
        print('All formats:')
        for i, fmt in enumerate(info.get('formats', [])):
            print(f"  {i}: {fmt.get('format_id')} | {fmt.get('ext')} | vcodec={fmt.get('vcodec', 'none')} | acodec={fmt.get('acodec', 'none')} | {fmt.get('url', 'N/A')[:80]}")
        print(f"\nTotal formats: {len(info.get('formats', []))}")
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
