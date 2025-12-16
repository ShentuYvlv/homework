import requests
import json
import time
import os
from concurrent.futures import ThreadPoolExecutor

# ================= 配置区域 =================
student_id = "2238328" # 你的学号
course_turn_id = 1110  # 选课轮次ID (来自抓包 courseSelectTurnAssoc)

base_api_url = "https://nbkjw.suibe.edu.cn/course-selection-api/api/v1/student/course-select"

# ！！！请务必替换为最新的抓包数据，401错误就是因为这里过期了！！！
headers = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Authorization": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXB3aXNkb20iLCJleHAiOjE3NjU5MDI5MzksInVzZXJuYW1lIjoiMjMwNjIyMDIifQ._RpH4NjjchNRC_LnYUjNQwD6i9AwNj7G_7mgrOv55yE",

    "Cookie": "arialoadData=false; ariauseGraymode=false; iPlanetDirectoryPro=yIHeOf1IzLezn1Uo9q0DAy; cs-course-select-student-token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXB3aXNkb20iLCJleHAiOjE3NjU5MDI5MzksInVzZXJuYW1lIjoiMjMwNjIyMDIifQ._RpH4NjjchNRC_LnYUjNQwD6i9AwNj7G_7mgrOv55yE",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
    "Referer": "https://nbkjw.suibe.edu.cn/course-selection/",
    "Origin": "https://nbkjw.suibe.edu.cn"
}

#经济分析与数学思维
lesson_ids = [
    361543, 361520, 361547, 361721, 361729, 361782, 361544, 361803,
    361725, 361545, 361553, 361780, 361766, 361518, 361776, 361542,
    361726, 361720, 361727, 361778,361781, 361730, 361779, 361775, 361728,
    361777, 361719, 361765, 361716
]

def process_lesson(lesson_id):
    """
    执行完整的选课流程：
    1. 预检查申请 (Predicate POST)
    2. 预检查结果 (Predicate GET)
    3. 正式选课申请 (Add Request POST)
    4. 正式选课结果 (Add Drop Response GET)
    """
    print(f"\n[Lesson {lesson_id}] >>> 开始流程")

    # ================= 阶段 1: 预检查 (Predicate) =================
    predicate_url = f"{base_api_url}/add-predicate"
    # 预检查时 virtualCost 通常为 0
    payload_step1 = {
        "studentAssoc": int(student_id),
        "courseSelectTurnAssoc": course_turn_id,
        "requestMiddleDtos": [{"lessonAssoc": lesson_id, "virtualCost": 0}],
        "coursePackAssoc": None
    }

    step1_uuid = post_request(predicate_url, payload_step1, lesson_id, "Step 1 (预检提交)")
    if not step1_uuid: return

    # 获取预检结果
    if not check_response_status(step1_uuid, lesson_id, "predicate-response", "Step 2 (预检结果)"):
        print(f"[Lesson {lesson_id}] 预检未通过或出现错误，停止后续步骤。")
        return

    # ================= 阶段 2: 正式选课 (Add Request) =================
    add_request_url = f"{base_api_url}/add-request"
    # 正式提交时 virtualCost 在抓包中显示为 null (Python中为None)
    payload_step3 = {
        "studentAssoc": int(student_id),
        "courseSelectTurnAssoc": course_turn_id,
        "requestMiddleDtos": [{"lessonAssoc": lesson_id, "virtualCost": None}],
        "coursePackAssoc": None
    }

    step3_uuid = post_request(add_request_url, payload_step3, lesson_id, "Step 3 (正式提交)")
    if not step3_uuid: return

    # 获取正式结果
    if check_response_status(step3_uuid, lesson_id, "add-drop-response", "Step 4 (最终结果)"):
        print(f"\n[!!!] 恭喜！课程 {lesson_id} 选课成功！ [!!!]\n")
        # 如果只需要选一门，可以在这里退出，或者继续选其他的
        # os._exit(0) 
    else:
        print(f"[Lesson {lesson_id}] 正式选课失败。")

def post_request(url, data, lesson_id, step_name):
    """通用 POST 请求发送器，返回任务 UUID"""
    try:
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code == 401:
            print(f"[ERROR] 401 未授权！Token已失效，请更新Headers。")
            os._exit(1)
        resp.raise_for_status()
        
        res_json = resp.json()
        if res_json.get("result") == 0 and res_json.get("data"):
            uuid = res_json["data"]
            print(f"[Lesson {lesson_id}] {step_name} 成功. UUID: {uuid}")
            return uuid
        else:
            print(f"[Lesson {lesson_id}] {step_name} 逻辑失败: {res_json}")
            return None
    except Exception as e:
        print(f"[Lesson {lesson_id}] {step_name} 请求异常: {e}")
        return None

def check_response_status(uuid, lesson_id, endpoint_type, step_name):
    """
    通用 GET 状态检查器
    endpoint_type: 'predicate-response' 或 'add-drop-response'
    """
    url = f"{base_api_url}/{endpoint_type}/{student_id}/{uuid}"
    
    # 稍微等待服务器处理 (轮询机制可以更复杂，这里简单sleep)
    time.sleep(0.8)

    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 401:
            print(f"[ERROR] 401 未授权！Token已失效。")
            os._exit(1)
        resp.raise_for_status()
        
        res_json = resp.json()
        data = res_json.get("data", {})
        
        # 核心判断逻辑：success 为 true
        if data.get("success") is True:
            print(f"[Lesson {lesson_id}] {step_name} 状态: 通过 (Success)")
            return True
        else:
            # 尝试提取错误信息
            err_msg = data.get("errorMessage")
            # 有时候具体的失败原因在 result 字段里
            detail_res = data.get("result", {})
            print(f"[Lesson {lesson_id}] {step_name} 状态: 失败/未通过. 原因: {err_msg} | 详情: {detail_res}")
            return False

    except Exception as e:
        print(f"[Lesson {lesson_id}] {step_name} 请求异常: {e}")
        return False

if __name__ == "__main__":
    print(f"Starting selection process for {len(lesson_ids)} courses...")
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(process_lesson, lesson_ids)
        
    print("\nAll tasks completed.")