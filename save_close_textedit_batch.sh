#!/bin/bash

# Script to save and close untitled TextEdit documents in small batches
# This approach processes one document at a time with delays to prevent freezing

# Create the directory if it doesn't exist
mkdir -p "/Users/thomasmulhern/unprocessed_textedits"

echo "Starting to process TextEdit documents..."

# Process documents one at a time
while true; do
    # Check if there are any documents left
    DOC_COUNT=$(osascript -e 'tell application "TextEdit" to count of documents' 2>/dev/null)
    
    if [ -z "$DOC_COUNT" ] || [ "$DOC_COUNT" -eq 0 ]; then
        echo "No more documents to process."
        break
    fi
    
    echo "Documents remaining: $DOC_COUNT"
    
    # Process only the first document
    osascript << 'EOF' 2>/dev/null
    tell application "TextEdit"
        if (count of documents) > 0 then
            try
                set current_doc to document 1
                set doc_name to name of current_doc
                
                -- Only process untitled documents
                if doc_name starts with "Untitled" then
                    -- Get document content
                    set doc_text to text of current_doc
                    
                    -- Extract first line for filename
                    set first_line to ""
                    if length of doc_text > 0 then
                        try
                            set first_line to paragraph 1 of doc_text
                            -- Clean up for filename
                            set first_line to do shell script "echo " & quoted form of first_line & " | sed 's/[^a-zA-Z0-9 ]//g' | sed 's/^ *//g' | sed 's/ *$//g' | tr ' ' '_' | cut -c1-50"
                        on error
                            set first_line to ""
                        end try
                    end if
                    
                    -- Generate filename
                    set timestamp to do shell script "date '+%Y%m%d_%H%M%S_%N'"
                    if length of first_line > 3 then
                        set filename to first_line & "_" & timestamp & ".txt"
                    else
                        set filename to "TextEdit_" & timestamp & ".txt"
                    end if
                    
                    set save_path to "/Users/thomasmulhern/unprocessed_textedits/" & filename
                    
                    -- Save and close
                    save current_doc in POSIX file save_path
                    close current_doc saving no
                    
                    return "Saved and closed: " & filename
                else
                    -- If it's not untitled, just close it
                    close current_doc saving no
                    return "Closed: " & doc_name
                end if
            on error error_message
                try
                    close document 1 saving no
                end try
                return "Error: " & error_message
            end try
        end if
    end tell
EOF
    
    # Small delay to prevent overwhelming the system
    sleep 0.1
done

echo "All documents processed successfully!"
echo "Files saved to: /Users/thomasmulhern/unprocessed_textedits/"