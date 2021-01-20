import re
from itertools import cycle, tee

import pandas as pd
from progress.bar import IncrementalBar


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def vessel_name(i, nextelem):

    vessel_sub_frame = df.iloc[i:nextelem]

    # extract vessel
    sentence = df.iloc[i][1]
    vessel_word_index = sentence.index("VESSEL")
    count_of_vessel = 7  # move to constant

    vessel_name_index = vessel_word_index + count_of_vessel
    vessel_name_buf = sentence[vessel_name_index:]

    return vessel_name_buf


def description_extraction(subdf, len_containers):
    # create dict with container number: description
    # descript_dict = {}

    sub_frame_of_bill_numbers = subdf[
        subdf["Unnamed: 0"].str.contains("[ЁёА-я]", regex=True) == True
    ]

    description_buf = []
    if len(sub_frame_of_bill_numbers["Unnamed: 0"]) == 1:
        # print("Thirst case")

        sentences = sub_frame_of_bill_numbers["Unnamed: 0"].values[0]
        # print(sentences)
        vessel_word_index = sentences.index("\n")
        description_buf_2 = sentences[:vessel_word_index]
        description_buf.append(description_buf_2)
        description_buf = description_buf * len_containers

    if (
        len(sub_frame_of_bill_numbers["Unnamed: 0"]) > 1
        and sub_frame_of_bill_numbers["Unnamed: 2"]
        .str.contains("Количество контейнеров")
        .any()
    ):
        # print("Second case")
        sentences = sub_frame_of_bill_numbers["Unnamed: 0"].values[0]
        vessel_word_index = sentences.index("\n")
        description_buf_2 = sentences[:vessel_word_index]
        description_buf.append(description_buf_2)
        description_buf = description_buf * len_containers

    elif (
        len(sub_frame_of_bill_numbers["Unnamed: 0"]) > 1
        and not sub_frame_of_bill_numbers["Unnamed: 2"]
        .str.contains("Количество контейнеров")
        .any()
    ):
        for z in range(len(sub_frame_of_bill_numbers["Unnamed: 0"])):
            # print("Third case")
            sentences = sub_frame_of_bill_numbers["Unnamed: 0"].values[z]
            # print(sentences)
            vessel_word_index = sentences.index("\n")
            description_buf_2 = sentences[:vessel_word_index]
            description_buf.append(description_buf_2)

    # to do fourth case, when last bill of the vessel has different descriptions of containers

    return description_buf


def excel_extractor(manifest_name):

    df = pd.read_excel("7065 MAERSK KAMPALA.xls")

    list_of_check = list(
        map(
            int,
            df[
                df["Unnamed: 2"].str.contains("Количество контейнеров:", regex=True)
                == True
            ]["Unnamed: 4"].values.tolist(),
        )
    )

    list_of_indexes_vessel = df[
        df["Unnamed: 1"].str.contains("VESSEL", regex=True) == True
    ].index.values.tolist()

    # add last element
    last_index = df.shape[0]

    list_of_indexes_vessel.append(last_index)

    # save result

    result = {
        "Type/Size": [],
        "Description": [],
        "Vessel": [],
        "Container Number": [],
        "Bill of Lading": [],
    }

    df_result = pd.DataFrame(
        result,
        columns=[
            "Type/Size",
            "Description",
            "Vessel",
            "Container Number",
            "Bill of Lading",
        ],
    )

    vessel_count = -1
    # VESSEL LOOP
    progress_vessel = len(
        df[df["Unnamed: 1"].str.contains("VESSEL", regex=True) == True].values
    )
    bar = IncrementalBar("Processing", max=progress_vessel)
    for i, nextelem in pairwise(list_of_indexes_vessel):

        # extract vessel
        vessel_sub_frame = df.iloc[i:nextelem]

        # extract vessel
        sentence = df.iloc[i][1]
        vessel_word_index = sentence.index("VESSEL")
        count_of_vessel = 7  # move to constant

        vessel_name_index = vessel_word_index + count_of_vessel
        vessel_name_buf = sentence[vessel_name_index:]
        # print(vessel_name_buf)

        # bill of lading loop of sub_frame
        list_of_indexes_bill_numbers = vessel_sub_frame[
            vessel_sub_frame["Unnamed: 0"].str.contains(
                "(^\d{9}$|^[a-zA-Z]{3}\d{6}$|^[a-zA-Z]{6}\d{3}$)", regex=True
            )
            == True
        ].index.values.tolist()

        list_of_indexes_bill_numbers.append(nextelem)
        # брать первый элемент следующей последовательности !!!

        bar.next()
        vessel_count += 1

        # BILL LOOP
        container_count = 0
        for k, nextelem_2 in pairwise(list_of_indexes_bill_numbers):

            bill_sub_frame = df.iloc[k:nextelem_2]

            # extract bill
            # print(
            #     "Bill of Lading Number: ", df.iloc[k]["Unnamed: 0"]
            # )  # save data to csv

            # container loops of subframe

            sub_containers_indexes_list = bill_sub_frame[
                bill_sub_frame["Unnamed: 3"].str.contains(
                    "^[a-zA-Z]{3}[uUjJzZ]{1}[0-9]{7}$", regex=True
                )
                == True
            ]["Unnamed: 3"]

            sub_container_indexes = sub_containers_indexes_list.index.values.tolist()
            sub_container_len = len(sub_container_indexes)

            # extract description
            description_buf = description_extraction(bill_sub_frame, sub_container_len)

            sub_container_indexes = sub_containers_indexes_list.index.values.tolist()

            # create dict for containers (container number: description)

            container_counter = 0

            # поиск
            for t in sub_containers_indexes_list.values:

                type_buf = df.iloc[sub_container_indexes[container_counter]][5]
                #    print(
                #       "Container number: ",
                #      t,
                #      " Type of Container: ",
                #      df.iloc[sub_container_indexes[container_counter]][5],
                #  )

                # print(df.iloc[sub_container_indexes[container_counter]])
                # if len(sub_frame_of_bill_numbers["Unnamed: 0"] > 1:

                # print("Container_counter: ", container_counter)
                # print("Common container_counter: ", container_count)

                result = {
                    "Type/Size": type_buf,
                    "Description": description_buf[container_counter],
                    "Vessel": vessel_name_buf,
                    "Container Number": t,
                    "Bill of Lading": df.iloc[k]["Unnamed: 0"],
                }

                # print(result)
                df_result = df_result.append(result, ignore_index=True)

                container_counter += 1
                container_count += 1

            if container_count == list_of_check[vessel_count]:
                # print(container_count)
                # print(
                "--------------------------------Everything is OK------------------------------------------------"
            # )

        # print("___________________________________________________________________")

    # save result
    bar.finish()
    output_filename = "output_1.xlsx"
    df_result.to_excel(output_filename)
    print("Файл Сохранен -", output_filename)
