import re
from tkinter import filedialog

import numpy as np
from flowio import create_fcs
import flowio
import glob, os
from pathlib import Path
import tkinter as tk
import time


def filter_file(path, channels, new_path):
    with open(path, 'rb') as fcs_file:
        flow_data = flowio.FlowData(fcs_file)
        data_array = np.reshape(flow_data.events, (-1, flow_data.channel_count))
    metadata = flow_data.text

    # get indices of requested channels
    flattened_channels_dict = {key: value['PnN'] for (key, value) in flow_data.channels.items()}
    channels_idx = [key for (key, value) in flattened_channels_dict.items() if value in channels]
    new_channels_idx = list(range(1, len(channels_idx) + 1))  # start from 1

    # filter data
    filtered_data_array = data_array[:, np.array(channels_idx).astype(int) - 1] # 1 to 0 index

    # change metadata
    idx_dict = {key: value for key, value in zip(channels_idx, new_channels_idx)}
    channel_info = {key: metadata[key] for key in metadata if bool(re.match(r"p\d.", key))}

    # Construct the regex pattern based on the digits to filter
    pattern = '|'.join(map(lambda x: f'(?<!\\d){x}(?!\\d)', channels_idx))
    pattern = f'({pattern})'

    filtered_channel_info = {key: metadata[key] for key in channel_info if bool(re.search(pattern, key))}
    filtered_and_renamed_channel_info = filtered_channel_info.copy()

    for key, value in filtered_channel_info.items():
        old_idx = re.findall(r'\d+', key)[0]
        new_idx = idx_dict[old_idx]
        new_idx = key.replace(str(old_idx), str(new_idx))
        filtered_and_renamed_channel_info[new_idx] = filtered_channel_info[key]
        if str(key) != str(new_idx):
            print(key, new_idx)
            del filtered_and_renamed_channel_info[key]

    new_meta = metadata.copy()
    [new_meta.pop(key) for key in channel_info.keys()]
    [new_meta.pop(key) for key in ['begindata', 'enddata']]

    new_meta.update(filtered_and_renamed_channel_info)

    # order channels according to metadata
    ordered_channels = [value for key, value in filtered_and_renamed_channel_info.items() if bool(re.match(r"p\dn", key))]

    fh = open(new_path, 'wb')
    create_fcs(fh, filtered_data_array.flatten(), ordered_channels, metadata_dict=new_meta)
    fh.close()

def main():
    channels_to_keep = [
        'FSC-A',
        'SSC-A',
        'SSC-B-A',
        'FSC-H',
        'SSC-H',
        'SSC-B-H',
        'B2-H',
        'B2-A',
        'Time',
        'Width'
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

    window.mainloop()


if __name__ == '__main__':
    main()