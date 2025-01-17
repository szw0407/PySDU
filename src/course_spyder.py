import httpx
import json
import bs4
from typing import Literal
from bkzhjx_login import interactive_login


def search_course(
    q: str,
    cookies: httpx.Cookies,
    course_type: Literal["Bx",  # 必修
                          "Xx", # 限选
                          "Ggxxk", # 公共选修课（任选）
                          "Faw"] = "Faw",  # 所有课程
    count: int = 100,
) -> httpx.Response:
    """
    Search course by keyword.
    """
    url = f"https://bkzhjx.wh.sdu.edu.cn/jsxsd/xsxkkc/xsxk{course_type}xk?1=1&kcxx={q}&skls=&skxq=&skjc=&endJc=&sfym=false&sfct=true&sfxx=true&skfs=&xqid="
    return httpx.post(
        url,
        data={
            "sEcho": "1",  # 页数
            "iColumns": "14",  # 列数
            "sColumns": "",  # 列名
            "iDisplayStart": "0",  # 起始位置
            "iDisplayLength": str(count),  # 结束位置
            "mDataProp_0": "kch",  # 课程号
            "mDataProp_1": "kcmc",  # 课程名称
            "mDataProp_2": "kchnew",  # 课程号
            "mDataProp_3": "dwmc",  # 开课单位名称
            "mDataProp_4": "jkfs",  # 讲课方式
            "mDataProp_5": "xmmc",  # 项目名称
            "mDataProp_6": "fzmc",  # 分组名称
            "mDataProp_7": "ktmc",  # 课题名称
            "mDataProp_8": "xf",  # 学分
            "mDataProp_9": "skls",  # 上课老师
            "mDataProp_10": "sksj",  # 上课时间
            "mDataProp_11": "skdd",  # 上课地点
            "mDataProp_12": "xqmc",  # 校区名称
            "mDataProp_13": "syrs",  # 剩余人数
            "mDataProp_14": "ctsm",  # 冲突
            "mDataProp_15": "czOper",  # 操作
        },
        cookies=cookies,
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "X-Requested-With": "XMLHttpRequest",
        },
    )

def choose_course(course_id: str, jx0404id: str, cookies: httpx.Cookies) -> httpx.Response:
    """
    Choose course by course_id and jx0404id.
    """
    print(course_id, jx0404id)
    return httpx.get(
        f'https://bkzhjx.wh.sdu.edu.cn/jsxsd/xsxkkc/xxxkOper?kcid={course_id}&jx0404id={jx0404id}',
        cookies=cookies,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Accept-Encoding": "gzip, deflate, br",
            'X-Requested-With': 'XMLHttpRequest',
        },
    )

if __name__ == "__main__":
    try:
        with open("bkzhjx_cookies.json", "r") as f:
            cookies = json.load(f)
            cookie = httpx.Cookies(cookies)
        page = httpx.get(
            r"https://bkzhjx.wh.sdu.edu.cn/jsxsd/framework/xsMainV_new.htmlx?t1=1",
            cookies=cookie,
        )
        assert page.status_code == 200
        assert bs4.BeautifulSoup(page.text, "html.parser").title.text != "登录"  # type: ignore
    except Exception as e:
        print("未找到有效cookies，将重新登录")
        cookie = interactive_login()
    else:
        print("cookies有效，免输入密码")
    q = input("请输入搜索关键词：")
    course_type = input("请输入课程类型（Bx 必修，Xx 限选，Ggxxk 公共选修课（任选），Faw 所有课程）：")  # type: ignore
    if not course_type in ["Bx", "Xx", "Ggxxk", "Faw"]:
        course_type:Literal['Bx','Xx','Ggxxk','Faw'] = "Faw"
    response:dict[str, list[dict[str, str]]] = search_course(q, cookie, course_type=course_type).json()
    # print(response.get('aaData', []))
    res = {}
    id = 0
    print('搜索结果\n序号\t课程名称\t授课班级\t项目名称\t上课时间\t课程性质\t考核方式\t上课地点\t剩余人数\t学分\t')
    for items in response.get('aaData', []):
        id += 1
        print(id, end=' ')
        print(items.get('kcmc', ''), items.get('ktmc', ''),items.get('xmmc',''), items.get('sksj', ''), items.get('kcxzmc', ''), items.get('khfs', ''), items.get('skdd', ''), items.get('syrs', ''), items.get('xf', ''))
        res[id] = items
    items = res[int(input("请输入课程序号："))]
    while True:
        a = choose_course(items.get('kch', ''),items.get('jx0404id',''), cookie)
        # print(a.text)
        if a.json().get('success', False):
            print("选课成功")
            break
        print("选课失败，重试中，按ctrl+c退出")

