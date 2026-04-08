import os
import subprocess
import sys

def main():
    """
    Script to automatically generate HTML documentation for the 'src' directory
    using the 'pdoc' library.
    """
    print("Generating documentation...")
    try:
        import pdoc
    except ImportError:
        print("pdoc not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pdoc3"])
    
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)

    src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
    
    # Run pdoc command targeting core files to avoid legacy namespace collision
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.dirname(os.path.dirname(__file__))
    subprocess.check_call([sys.executable, "-m", "pdoc", "--html", "--output-dir", docs_dir, os.path.join(src_dir, "agent", "main_enterprise.py"), os.path.join(src_dir, "backend", "main.py"), "--force"], env=env)
    
    print(f"Documentation generated successfully in {docs_dir}")

if __name__ == "__main__":
    main()
