import subprocess

# টেস্ট ইনপুট
command = ["python", "../run_model.py", "--model", "deepseek-coder-1.3b", "--input", "Hello, how are you?"]

result = subprocess.run(command, capture_output=True, text=True)
print("=== CLI Test Result ===")
print("Return code:", result.returncode)
if result.returncode == 0:
    print("✅ CLI test passed - script executed successfully")
else:
    print("❌ CLI test failed")
    print("STDERR:")
    print(result.stderr)