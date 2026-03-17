from wakepy import keep

with keep.presenting():
    # Your long-running code goes here
    print("Fedora will stay awake as long as this block is running.")
    import time
    time.sleep(7200)  # Example: 2 hour task

print("Script finished. Fedora can now sleep according to system settings.")