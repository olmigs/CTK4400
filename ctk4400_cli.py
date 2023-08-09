import json
import pathlib
import typer
import dw7_to_wav as dtw
# import tw7_to_wav as ttw
import wav_to_dw7 as wtd
# import wav_to_tw7 as wtt

app = typer.Typer()

@app.command()
def wtd_wrapper(json_path: str, output_path: str, slot: int = 1):
    print(f"What're you doing with {json_path}?")
    # 1. Read JSON to STRUCT-like (hash table)
    with open(json_path, "r") as json_file:
        struct = json.load(json_file)
        # print(struct)
        # 2. Pass to wtd.wav_to_dw7
        wtd.wav_to_dw7(struct, pathlib.Path(output_path), slot)

@app.command()
def dtw_wrapper(input_path: str, output_path: str):
    dtw.dw7_to_wav(pathlib.Path(input_path), pathlib.Path(output_path))

if __name__ == "__main__":
    app()