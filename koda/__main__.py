import dearpygui.dearpygui as dpg
import dearpygui.demo as demo


def main():
    dpg.create_context()
    dpg.create_viewport(title="KODA - Koder arytmetyczny", height=400, width=600)
    dpg.setup_dearpygui()

    def encode_callback(sender, app_data):
        print(app_data)
        paths = [path for file_name, path in app_data["selections"].items()]
        if paths:
            dpg.set_value("encode_label", "\n".join(paths))
            dpg.show_item("group_encoding")
            dpg.set_value("progressbar_encoding", 0)
        else:
            dpg.set_value("encode_label", None)
            dpg.hide_item("group_encoding")

    def decode_callback(sender, app_data):
        print(sender, app_data)

    with dpg.file_dialog(
        directory_selector=False,
        show=False,
        callback=encode_callback,
        tag="file_dialog_encode",
        file_count=1,
        modal=True,
        height=400,
        width=600,
    ):
        dpg.add_file_extension(".*")

    with dpg.file_dialog(
        directory_selector=False,
        show=False,
        callback=decode_callback,
        tag="file_dialog_decode",
        modal=True,
        height=400,
        width=600,
    ):
        dpg.add_file_extension(".arencoded")

    with dpg.window(
        label="KODA - Kodowanie arytmetyczne",
        tag="primary",
        height=400,
        width=600,
        no_move=True,
        no_close=True,
        no_collapse=True,
    ):
        with dpg.tab_bar():
            with dpg.tab(label="Encode file"):
                dpg.add_separator()
                with dpg.group(horizontal=True):
                    dpg.add_text(default_value="No file selected", tag="encode_label")
                    dpg.add_button(
                        label="Select file to encode",
                        callback=lambda: dpg.show_item("file_dialog_encode"),
                    )

                with dpg.group(show=False, tag="group_encoding", horizontal=True):
                    dpg.add_progress_bar(
                        label="Encoding...", tag="progressbar_encoding"
                    )
                    dpg.add_button(label="Encode!")

            with dpg.tab(label="Decode file"):
                dpg.add_text(tag="decode_label")
                dpg.add_button(
                    label="Select file to decode",
                    callback=lambda: dpg.show_item("file_dialog_decode"),
                    tag="compress",
                )

    dpg.show_viewport()
    dpg.set_primary_window("primary", True)
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
