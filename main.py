from youtube_transcript_api import YouTubeTranscriptApi
import tkinter as tk
import openai


def merge_transcripts(t1, t2):
    merge =  f"""
    The following are two transcript summaries. You must combine them into a single summary.

    First:
    {t1}

    Second:
    {t2}
    """.strip()
    print("-------- merging transcripts --------")
    print(merge)
    print("-------- ------------------- --------")
    return merge


def summarize_transcript(transcript, api_key):
    try:
        full_text = transcript
        if type(transcript) != str:
            full_text = ' '.join(snip['text'] for snip in transcript)
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {
                    'role': 'system',
                    'content': 'Summarize the following video transcript. Outline the main points and themes.'
                },
                {
                    'role': 'user',
                    'content': full_text
                }],
            max_tokens=1000,
            frequency_penalty=0.0)
        return response['choices'][0]['message']['content']
    except openai.error.InvalidRequestError:
        return summarize_transcript(merge_transcripts(summarize_transcript(transcript[:len(transcript) // 2 - 1], api_key),
                                                      summarize_transcript(transcript[len(transcript) // 2:], api_key)), api_key)


def summarize_video(video_id, text_widget, api_key_entry):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    summary = summarize_transcript(transcript, api_key_entry.get())
    text_widget.delete(1.0, tk.END)
    text_widget.insert(tk.END, summary)


def main():
    root = tk.Tk()
    root.title("YouTube Video Summary")
    root.geometry("400x500")

    # OpenAI Key
    tk.Label(root, text="OpenAI Key:").grid(row=0, sticky='w')
    api_key_entry = tk.Entry(root)
    api_key_entry.grid(row=1, sticky='w')
    api_key_entry.focus()

    # YouTube Video ID
    tk.Label(root, text="YouTube Video ID:").grid(row=2, sticky='w')
    video_id_entry = tk.Entry(root)
    video_id_entry.grid(row=3, sticky='w')
    video_id_entry.focus()

    # Result
    tk.Label(root, text="Summary:").grid(row=4, sticky='w')
    summary_text = tk.Text(root, wrap='word')
    summary_text.grid(row=5, sticky='news')

    # Scrollbar
    scrollb = tk.Scrollbar(root, command=summary_text.yview)
    scrollb.grid(row=5, column=1, sticky='ns')
    summary_text.configure(yscrollcommand=scrollb.set)

    # Configure grid
    root.grid_rowconfigure(3, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Button
    tk.Button(root, text="Summarize",
              command=lambda: summarize_video(video_id_entry.get(), summary_text, api_key_entry)).grid(row=6,
                                                                                                       sticky='w')

    root.mainloop()


if __name__ == "__main__":
    main()
