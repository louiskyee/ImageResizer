import gradio as gr
import cv2
import numpy as np
from PIL import Image
import io

def is_valid_image(file):
    """檢查是否為有效的圖片格式"""
    valid_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']
    return any(file.name.lower().endswith(fmt) for fmt in valid_formats)

def resize_image(input_image, resize_method, scale_factor=None, target_width=None, target_height=None, quality=90):
    """調整圖片尺寸的主要函數"""
    if input_image is None:
        return None, "請上傳圖片"

    try:
        # 如果輸入是 PIL Image，直接使用
        if isinstance(input_image, Image.Image):
            img = input_image
        else:
            # 如果是 numpy array，轉換為 PIL Image
            img = Image.fromarray(input_image)

        # 確保圖片為 RGBA 模式（透明通道）
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        original_width, original_height = img.size

        # 根據選擇的方式調整大小
        if resize_method == "比例調整":
            if scale_factor is None or scale_factor <= 0:
                return None, "請輸入有效的縮放比例"
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
        else:  # 自訂尺寸
            if not target_width or not target_height or target_width <= 0 or target_height <= 0:
                return None, "請輸入有效的寬度和高度"
            new_width = target_width
            new_height = target_height

        # 調整圖片大小
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 保存為 PNG 格式
        output_buffer = io.BytesIO()
        resized_img.save(output_buffer, format='PNG')
        output_buffer.seek(0)

        # 將 PNG 圖片轉回 PIL Image 並轉為 numpy array
        output_img = Image.open(output_buffer)
        output_image = np.array(output_img)

        # 回傳調整後的圖片和資訊訊息
        info_message = f"原始尺寸: {original_width}x{original_height}\n調整後尺寸: {new_width}x{new_height}\n已保存為 PNG 格式"
        return output_image, info_message

    except Exception as e:
        return None, f"處理圖片時發生錯誤：{str(e)}"

# 創建Gradio界面
def create_interface():
    with gr.Blocks(title="圖片尺寸調整工具", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 圖片尺寸調整工具")

        with gr.Row():
            with gr.Column():
                # 輸入區域
                input_image = gr.Image(type="pil", label="上傳圖片")
                resize_method = gr.Radio(
                    choices=["比例調整", "自訂尺寸"],
                    value="比例調整",
                    label="調整方式"
                )

                with gr.Group() as scale_group:
                    scale_factor = gr.Slider(
                        minimum=0.1,
                        maximum=5.0,
                        value=1.0,
                        step=0.1,
                        label="縮放比例"
                    )

                with gr.Group() as custom_size_group:
                    target_width = gr.Number(label="目標寬度(像素)", precision=0)
                    target_height = gr.Number(label="目標高度(像素)", precision=0)

                quality = gr.Slider(
                    minimum=1,
                    maximum=100,
                    value=90,
                    step=1,
                    label="輸出品質(1-100)"
                )

                submit_btn = gr.Button("開始處理", variant="primary")

            with gr.Column():
                # 輸出區域
                output_image = gr.Image(label="調整後的圖片")
                info = gr.Textbox(label="處理資訊", lines=2)

        # 事件處理
        def update_visibility(choice):
            if choice == "比例調整":
                return gr.update(visible=True), gr.update(visible=False)
            else:
                return gr.update(visible=False), gr.update(visible=True)

        resize_method.change(
            fn=update_visibility,
            inputs=resize_method,
            outputs=[scale_group, custom_size_group]
        )

        # 提交按鈕事件
        submit_btn.click(
            resize_image,
            inputs=[
                input_image,
                resize_method,
                scale_factor,
                target_width,
                target_height,
                quality
            ],
            outputs=[output_image, info]
        )

        # 使用說明
        gr.Markdown("""
        ## 使用說明
        1. 上傳圖片：支援 JPG、PNG、BMP、WebP 格式
        2. 選擇調整方式：
           - 比例調整：按照原始尺寸等比例縮放
           - 自訂尺寸：指定具體的寬度和高度
        3. 輸出格式：所有圖片都會自動轉換為 PNG 格式（支援透明通道）
        4. 點擊「開始處理」進行轉換
        5. 處理完成後可直接下載調整後的圖片

        ## 注意事項
        - 建議使用適當的縮放比例，過度放大可能導致圖片模糊
        - 自訂尺寸可能會改變圖片的原始比例
        - 較大的圖片可能需要較長處理時間
        """)

    return app

# 啟動應用
if __name__ == "__main__":
    app = create_interface()
    app.launch(share=True)