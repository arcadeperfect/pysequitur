from pysequitur.file_sequence import Item, Parser



def test_item_set_padding(create_files_from_list):
   
    # test unlinked item
   
    item = Item(
        prefix="render",
        delimiter=".",
        frame_string="101",
        extension="exr",
        directory= None
    )

    assert item.prefix == "render"
    assert item.delimiter == "."
    assert item.frame_string == "101"
    assert item.extension == "exr"



    item.padding = 4

    assert item.prefix == "render"
    assert item.delimiter == "."
    assert item.frame_string == "0101"
    assert item.extension == "exr"

    item.padding = 1

    assert item.padding == 3
    assert item.frame_string == "101"

    item.padding = 10

    assert item.padding == 10
    assert item.frame_string == "0000000101"

    # test linked item

    file = create_files_from_list(["image.0056.exr"])[0]

    item = Parser.item_from_filename(file)

    assert item.padding == 4
    assert item.frame_string == "0056"

    item.padding = 3

    assert item.padding == 3
    assert item.frame_string == "056"



    file = create_files_from_list(["render.123_final.exr"])[0]

    item = Parser.item_from_filename(file)

    assert item.padding == 3
    assert item.frame_string == "123"

    item.padding = 6

    assert item.padding == 6
    assert item.frame_string == "000123"


    file = create_files_from_list(["botty_0000304104_final.exr"])[0]

    item = Parser.item_from_filename(file)

    assert item.padding == 10
    assert item.frame_string == "0000304104"

    item.padding = 1

    assert item.padding == 6
    assert item.frame_string == "304104"

    item.padding = 30

    assert item.padding == 30
    assert item.frame_string == "000000000000000000000000304104"