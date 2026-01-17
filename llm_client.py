from openai import OpenAI

# API_BASE_URL = "https://api.deepseek.com/v1"
# API_KEY = "sk-0ac41e30523449c0bb54b3be0436b978"

API_BASE_URL = "https://api.siliconflow.cn/v1/"
API_KEY = "sk-dnuiwhftndgzvbefpkwixvxkoovvpsbpomtadknhplakivtt"

class LLMClient:
    def __init__(self, api_key=API_KEY, base_url=API_BASE_URL):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
    def chat(self, messages, temperature=0.5, stream=True, on_chunk=None, print_stream=True):
        try:
            response = self.client.chat.completions.create(
                model="Pro/deepseek-ai/DeepSeek-V3", # deepseek-chat Pro/deepseek-ai/DeepSeek-V3
                messages=messages,
                temperature=temperature,
                stream=stream
            )
            
            if stream:
                full_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        if print_stream:
                            print(content, end="", flush=True)
                        if on_chunk is not None:
                            on_chunk(content)
                        full_response += content
                if print_stream:
                    print()
                return full_response
            else:
                return response.choices[0].message.content
                
        except Exception as e:
            print(f"LLM调用出错: {str(e)}")
            raise

# 使用示例
if __name__ == "__main__":
    llm = LLMClient()
    messages = [
        {"role": "user", "content": "你好"}
    ]
    response = llm.chat(messages)
    print(f"响应: {response}")
