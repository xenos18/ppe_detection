def get_bb(img, coords):
    result = []
    for i in coords:
        if len(i) == 58:
            result.append(check_mask(img, i))
            result.append(check_sweater(img, i))
    return result


def check_mask(img, coords):
    mask_x1 = int(coords[19])
    mask_y1 = int(coords[8])
    mask_x2 = int(coords[16])
    mask_y2 = mask_y1 + (int(coords[26]) - int(coords[8]))//2
    sum_r, sum_g, sum_b = 0, 0, 0
    count = 0
    for i in range(len(img)):
        for j in range(len(img[i])):
            if mask_y1 <= i <= mask_y2 and mask_x1 <= j <= mask_x2:
                rgb = img[i][j]
                sum_r += rgb[0]
                sum_g += rgb[1]
                sum_b += rgb[2]
                # print('Координады:', j, i)
                # print('Найден пиксель:', rgb)
                count += 1
    try:
        result = [sum_r // count, sum_g // count, sum_b // count]
        if sum(result) >= 300:
            return [mask_x1, mask_y1, mask_x2, mask_y2, 1]
        else:
            return [mask_x1, mask_y1, mask_x2, mask_y2, 0]
    except ZeroDivisionError:
        pass


def check_sweater(img, coords):
    sw_x1 = int(coords[25])
    sw_y1 = int(coords[26])
    sw_x2 = int(coords[22])
    sw_y2 = int(coords[-2])
    sum_r, sum_g, sum_b = 0, 0, 0
    count = 0
    for i in range(len(img)):
        for j in range(len(img[i])):
            if sw_y1 <= i <= sw_y2 and sw_x1 <= j <= sw_x2:
                rgb = img[i][j]
                sum_r += rgb[0]
                sum_g += rgb[1]
                sum_b += rgb[2]
                # print('Координады:', j, i)
                # print('Найден пиксель:', rgb)
                count += 1
    try:
        result = [sum_r // count, sum_g // count, sum_b // count]
        if sum(result) >= 350:
            return [sw_x1, sw_y1, sw_x2, sw_y2, 1]
        else:
            return [sw_x1, sw_y1, sw_x2, sw_y2, 0]
    except ZeroDivisionError:
        pass