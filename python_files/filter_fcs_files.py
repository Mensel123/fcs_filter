from tkinter import filedialog

import flowkit as fk
import glob, os
from pathlib import Path
import tkinter as tk
import time


def filter_file(path, channels, new_path):
    sample = fk.Sample(path, ignore_offset_error=True)
    metadata = sample.get_metadata()
    print(metadata)

    # Filter
    df = sample.as_dataframe(source='raw')
    df_filtered = df[channels]

    # Save as new file
    sample_filtered = fk.Sample(df_filtered, sample_id='filtered_data')
    sample_filtered.metadata = metadata
    sample_filtered.export(new_path, source='raw', include_metadata=True)

    del sample


def main():
    # path = '/Users/mendelengelaer/Documents/AMC/promotie.nosync/scripts/fsc_file_filter/test_data'
    # new_path = '/Users/mendelengelaer/Documents/AMC/promotie.nosync/scripts/fsc_file_filter/filtered_test_data'

    channels_to_keep = [
        'FSC-A',
        'SSC-A',
        'SSC-B-A',
        'B2-A',
        'B4-A',
        'R1-A',
        'R2-A',
        'V3-A',
        'V5-A',
        'Time'
    ]

    window = tk.Tk()
    path = tk.StringVar()
    new_path = tk.StringVar()
    status = tk.StringVar()

    window.title('FCS File Filter')
    window.geometry('350x200')

    def browse_root_button():
        selected_path = filedialog.askdirectory()
        print(selected_path)
        path.set(selected_path)

    def browse_new_root_button():
        selected_path = filedialog.askdirectory()
        new_path.set(selected_path)

    def run():
        status.set('Running')
        try:
            loop_through_files(channels_to_keep, new_path.get(), path.get())
        except Exception as e:
            status.set('Error')
            tk.messagebox.showerror(message=f'error: {e}')

    def loop_through_files(channels_to_keep, new_path, path):
        for filename in glob.iglob(f"{path}/**", recursive=True):
            if '.fcs' in filename:
                new_rel_path = os.path.relpath(filename, path)
                new_sample_path = os.path.join(new_path, new_rel_path)
                new_sample_path = new_sample_path.replace("\\", "/")
                new_sample_dir = new_sample_path.rsplit('/', 1)[0]

                print(new_sample_path)

                Path(new_sample_dir).mkdir(parents=True, exist_ok=True)

                filter_file(filename, channels_to_keep, new_sample_path)
            time.sleep(1)
        status.set('Done')

    btn = tk.Button(window, text='Select root', bg='orange', fg='red', command=browse_root_button)
    btn.pack()

    path.set('No root path selected')
    root_label = tk.Label(window, textvariable=path, fg='red')
    root_label.pack()

    btn = tk.Button(window, text='Select new root', bg='orange', fg='red', command=browse_new_root_button)
    btn.pack()

    new_path.set('No filtered root path selected')
    new_root_label = tk.Label(window, textvariable=new_path, fg='red')
    new_root_label.pack()

    btn = tk.Button(window, text='Run', bg='orange', fg='red', command=run)
    btn.pack()

    status.set('Idle')
    status_label = tk.Label(window, textvariable=status, bg='orange', fg='red')
    status_label.pack()

    # folder_selected = filedialog.askdirectory()

    window.mainloop()


if __name__ == '__main__':
    main()