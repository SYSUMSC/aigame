# 任务介绍

随着科技的发展，数字图像在各个领域中的应用越来越广泛，如医疗影像、监控安防、航空航天等。然而，在图像采集、传输和存储过程中，往往会受到多种噪声的干扰，导致图像质量下降，影响后续的图像处理和分析。因此，图像降噪技术在许多领域具有重要的研究意义和应用价值。

参赛者需利用人工智能技术，对给定的含噪图片进行降噪处理，使其尽可能接近原始清晰图像。

# 比赛数据

`task-dataset` 文件夹下有训练图片数据及降噪标签 5 对。每张照片均为彩色照片，且大小不一。

本赛题的图片噪声可以近似**高斯噪声**来分析。

# 测试数据

`test-dataset` 文件夹下有测试图片数据 1 张，对应的降噪标签需要参赛者给出。

# 结果提交

(说明一下结果的提交方式，`answer.json` 的组织方式)

# 评价指标

本赛题计算参赛者给出的降噪图片与原图片的 MSELoss 的累积和作为本次结果提交的 Loss，Loss 越低表示效果越好。

# 评分规则解释及评测脚本

本赛题会依次读取参赛者给出的降噪图片与原图片，将其转换为 np.ndarray 格式，依次计算每对图片的 MSELoss 并累加为最终结果，相关脚本如下。

```Python
def mse_loss(answer_image, label_image):
    loss = ((answer_image - label_image) ** 2).mean()
    return loss

def cal_score():
    answer_images = get_answer_images()
    labels_images = get_labels_images()
    score = 0.0
    for answer_image, label_image in zip(answer_images, labels_images):
        loss = mse_loss(answer_image, label_image)
        score += loss
    return score
```