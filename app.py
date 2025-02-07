from flask import Flask, request, jsonify
import face_recognition
import numpy as np
import json

app = Flask(__name__)
# 设置最大上传文件大小（50MB）
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
# 让 Flask 全局返回 JSON 时不转义中文
app.json.ensure_ascii = False


@app.route("/create_face_model", methods=["POST"])
def create_face_model():
    """创建人脸模型"""
    file = request.files.get("image")
    user_id = request.form.get("user_id")
    if not file or not user_id:
        return jsonify({"error": "Missing image or user_id"}), 400
    # 读取图片
    image = face_recognition.load_image_file(file)
    encodings = face_recognition.face_encodings(image)
    if not encodings:
        return jsonify({"error": "未检测到人脸"}), 400
    if len(encodings) > 1:
        return jsonify({"error": "检测到多张人脸"}), 400
    # 把所有人脸的特征向量转换成 JSON 格式（列表的列表）
    face_encoding = encodings[0].tolist()
    return (
        jsonify(
            {
                "message": "人脸模型已创建",
                "user_id": user_id,
                "face_encoding": face_encoding,
            }
        ),
        200,
    )


@app.route("/recognize_face", methods=["POST"])
def recognize_face():
    """识别人脸模型"""
    file = request.files.get("image")
    user_id = request.form.get("user_id")
    face_encoding_str = request.form.get("face_encoding")
    if not file:
        return jsonify({"error": "缺少图像文件"}), 400
    image = face_recognition.load_image_file(file)
    encodings = face_recognition.face_encodings(image)
    if not encodings:
        return jsonify({"error": "未检测到人脸"}), 400
    if len(encodings) > 1:
        return jsonify({"error": "检测到多张人脸"}), 400
    
    try:
        face_encoding_np = np.array(json.loads(face_encoding_str))
    except (json.JSONDecodeError, ValueError):
        return jsonify({"error": "人脸编码格式错误"}), 400

    # 确保 face_encoding_np 形状正确
    if face_encoding_np.shape != (128,):
        return jsonify({"error": "人脸编码数据格式不正确"}), 400
    
    # 进行人脸匹配
    known_face_encoding = np.array(encodings[0])
    match_results = face_recognition.compare_faces([known_face_encoding],face_encoding_np) # 传入一个列表
    distance = face_recognition.face_distance([known_face_encoding],face_encoding_np)[0]  # 计算欧氏距离
    
    match_result = bool(match_results[0])  # 转换为 Python 原生布尔类型
    distance_value = float(distance)  # 转换为 Python 原生 float 类型
    
    return (
        jsonify(
            {
                "match": match_result,  # True / False
                "distance": distance_value,  # 识别距离，越小越相似
                "message": "匹配成功" if match_result else "匹配失败",
            }
        ),
        200
    )


if __name__ == "__main__":
    app.run(debug=True)
