import os.path

import pandas as pd
import matplotlib.pyplot as plt
import random
import math


# functions

def handle_files():
    file = open("./files/car_evaluation.data")

    i = 0

    lines = file.readlines()

    random.shuffle(lines)

    ce_trn = os.path.isfile('./files/cars_evaluation.trn')
    ce_tst = os.path.isfile('./files/cars_evaluation.tst')
    cef_tst = os.path.isfile('./files/cars_evaluation_format.tst')

    if ce_trn and ce_tst and cef_tst:
        trn = open("./files/cars_evaluation.trn", "w")
        tst = open("./files/cars_evaluation.tst", "w")
        tst_format = open("./files/cars_evaluation_format.tst", "w")
    else:
        trn = open("./files/cars_evaluation.trn", "x")
        tst = open("./files/cars_evaluation.tst", "x")
        tst_format = open("./files/cars_evaluation_format.tst", "x")

    # trn.write("Class,Price,Performance,Reliability,Acceptance\n")
    # tst.write("Class,Price,Performance,Reliability,Acceptance\n")

    for x in lines:
        if i <= len(lines) * 0.7:
            trn.write(x)
        elif i > len(lines) * 0.3:
            tst.write(x)
            tst_format.write(x.rsplit(',', 1)[0] + '\n')
        i += 1

    trn.close()
    tst.close()
    tst_format.close()


def show_graph():
    exists = os.path.isfile('./files/after.csv')

    if exists:
        after = open("./files/after.csv", "w")
    else:
        after = open("./files/after.csv", "x")

    after.write("Class,Price,Performance,Reliability,Acceptance\n")

    f = open("./files/cars_evaluation.tst")

    before_csv = os.path.isfile('./files/before.csv')
    if before_csv:
        before = open("./files/before.csv", "w")
    else:
        before = open("./files/before.csv", "x")

    before.write("Class,Price,Performance,Reliability,Acceptance\n")

    for line in f:
        before.write(line)

    before.close()

    i = 0
    for car in tst_format:
        after.write(car.rsplit(',', 1)[0] + "," + assigned[i] + '\n')
        i += 1

    after.close()

    df = pd.read_csv('./files/before.csv')

    df = df.groupby(['Acceptance']).size()
    df.plot(kind='bar', title='Original data', ylim=(0, 400))

    plt.show()

    df = pd.read_csv('./files/after.csv')

    df = df.groupby(['Acceptance']).size()
    df.plot(kind='bar', title='New data', ylim=(0, 400))

    plt.show()


def check_accuracy(l):
    assigned = open("./files/cars_evaluation.tst")

    cars = assigned.readlines()

    val = len(cars)

    count = 0
    i = 0
    for label in cars:
        if label[:-1].rsplit(',')[-1] == l[i]:
            count += 1
        i += 1
    acc = (count / val) * 100
    return acc


def get_avg_acc(acc):
    sum = 0
    for val in acc:
        sum += val

    avg = sum / len(acc)
    return int(avg)


def get_deviation(acc):
    avg = get_avg_acc(acc)
    sum = 0

    for val in acc:
        sum += pow((int(val) - avg), 2)

    deviation = math.sqrt(sum / len(acc))

    return deviation


def calculate_probability(car, keyword):
    probability = 1

    index = 0
    for word in car.split(','):
        a_c = check_both(word, keyword, index)
        key_count = count_word(keyword)

        # laplace

        if a_c == 0 or key_count == 0:
            a_c = 1
            key_count = key_count + count_specific_word(keyword, index)

        probability *= (a_c / key_count)
        index += 1

    return probability


def check_both(w1, w2, i):
    count = 0
    for c in trn_format:
        if w1 in c.split(',')[i] and w2 in c.split(',')[6]:
            count += 1
    return count


def count_specific_word(w, i):
    count = 0
    for c in trn_format:
        if w in c.split(',')[i]:
            count += 1
    return count


def count_word(w):
    count = 0
    for c in trn_format:
        if w in c:
            count += 1
    return count


cycle = 0

acc = []

while cycle != 10:

    print("Computing...")

    print("Cycle:", cycle)

    handle_files()

    trn = open("./files/cars_evaluation.trn")
    tst = open("./files/cars_evaluation.tst")

    trn_format = []
    tst_format = []

    # fill list with car annotations

    for word in trn:
        trn_format.append(word[:-1])
    for word in tst:
        tst_format.append(word[:-1])

    trn.close()
    tst.close()

    # logic

    assigned = []

    for car in tst_format:
        values = {}

        # unacc angle

        unacc_probability = calculate_probability(car, "unacc")

        values.update({"unacc": unacc_probability})

        # acc angle

        acc_probability = calculate_probability(car, "acc")

        values.update({"acc": acc_probability})

        # good angle

        good_probability = calculate_probability(car, "good")

        values.update({"good": good_probability})

        # vgood angle

        vgood_probability = calculate_probability(car, "vgood")

        values.update({"vgood": vgood_probability})

        # print decision

        max_key = max(values, key=values.get)

        assigned.append(max_key)

    print("Accuracy:" + str(int(check_accuracy(assigned))) + "%")

    acc.append(check_accuracy(assigned))

    # show_graph()

    cycle += 1

print("Done computing.")
print("Average accuracy: " + str(get_avg_acc(acc)) + '%')
print("Standard deviation: " + str(get_deviation(acc)))
