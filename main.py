import os
import re
import tkinter as tk
import cadquery as cq
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


def main():
    client = genai.Client()
    window = tk.Tk()
    window.title("3D modell generator")
    window.geometry("500x350")

    tk.Label(window, text="3D modell generátor", font=("Arial", 14)).pack(
        pady=10
    )
    client_model_entry = tk.Entry(window, width=50)
    client_model_entry.pack(pady=10)

    status_label = tk.Label(window, text="")
    status_label.pack(pady=10)

    system_prompt = "Output ONLY valid Python code using CadQuery inside a single markdown code block. Ensure the final object is assigned to a variable named 'result'."

    def generating():
        user_input = client_model_entry.get()
        if not user_input:
            status_label.config(text="Kérlek, írj be egy leírást!", fg="red")
            return

        status_label.config(text="Generálás...", fg="orange")
        window.update_idletasks()

        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=user_input,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt, temperature=0.2
                ),
            )

            raw_code = re.search(r"```python(.*?)```", response.text, re.DOTALL)
            clean_code = raw_code.group(1).strip() if raw_code else response.text.strip()

            local_vars = {"cq": cq}
            exec(clean_code, {}, local_vars)

            if "result" in local_vars:
                cq.exporters.export(local_vars["result"], "modell.stl")
                status_label.config(text="Sikeres mentés: modell.stl", fg="green")
            else:
                status_label.config(text="Hiba: nincs 'result' változó.", fg="red")

        except Exception as e:
            status_label.config(text="Hiba történt a futtatás során.", fg="red")
            print(e)

    tk.Button(
        window, text="Generálás", command=generating, bg="green", fg="white"
    ).pack(pady=10)

    window.mainloop()


if __name__ == "__main__":
    main()