"""
测试试算接口是否正常工作
"""
import requests
import json

# 测试URL
url = "http://127.0.0.1:8000/api/v1/test-trial/trial-calculate"

# 测试数据
test_data = {
    "amount": 200,
    "min_period": 14,
    "stage_num": 2,
    "daily_interest_rate": 9,
    "daily_fee_rate": 103,
    "float_rate": 94,
    "tax_rate": 16,
    "coupon_amount": 0,
    "reduce_rate": 0
}

print("=" * 80)
print("测试试算接口")
print("=" * 80)
print(f"\n请求URL: {url}")
print(f"请求数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
print("\n" + "-" * 80)

try:
    # 发送POST请求（注意：实际使用时需要携带认证token）
    response = requests.post(url, json=test_data)
    
    print(f"\n响应状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ 请求成功！")
        print(f"响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
    elif response.status_code == 401:
        print(f"\n⚠️  需要认证（这是正常的，因为接口需要登录）")
        print(f"响应: {response.text}")
    elif response.status_code == 404:
        print(f"\n❌ 接口不存在（404）")
        print(f"响应: {response.text}")
        print("\n请检查：")
        print("1. 后端服务是否已重启")
        print("2. app/api/router.py 中是否已注册 test_trial 路由")
    else:
        print(f"\n❌ 请求失败")
        print(f"响应: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ 连接失败！")
    print("请确保后端服务正在运行：python main.py")
except Exception as e:
    print(f"\n❌ 发生错误: {str(e)}")

print("\n" + "=" * 80)
