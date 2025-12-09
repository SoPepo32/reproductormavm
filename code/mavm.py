import subprocess
import json
import os

class MaVM:
    def extrac_type_all(file, output_folder, content_type=None):
        resultado = subprocess.run(
            ["mkvmerge", "--identification-format", "json", "--identify", file],
            capture_output=True,
            text=True
        )
        print("STDOUT:", resultado.stdout)
        print("STDERR:", resultado.stderr)
        contenido_json = json.loads(resultado.stdout)["attachments"]
        
        files = []
        for file_json in contenido_json:
            if content_type:
                if file_json["content_type"] == content_type:
                    files.append((file_json["id"],file_json["file_name"]))
            else:
                files.append((file_json["id"],file_json["file_name"]))
        
        os.makedirs(output_folder, exist_ok=True)
        files_path = []
        for file_id in files:
            print("mkvextract", "attachments", file, f"{file_id[0]}:{file_id[1]}")
            r = subprocess.run([
                "mkvextract", "attachments", file, f"{file_id[0]}:{file_id[1]}"
            ],
            cwd=output_folder,
            capture_output=True,
            text=True)
            print(r.stdout)
            files_path.append(os.path.join(output_folder, file_id[1]))
        return files_path