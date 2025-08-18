#!/bin/bash

# Script to save and close all untitled TextEdit documents
# This will save each untitled document in /Users/thomasmulhern/unprocessed_textedits/

# Create the directory if it doesn't exist
mkdir -p "/Users/thomasmulhern/unprocessed_textedits"

osascript << 'EOF'
tell application "TextEdit"
    repeat
        set doc_count to count of documents
        if doc_count = 0 then exit repeat
        
        try
            set current_doc to document 1
            set doc_name to name of current_doc
            
            -- Check if document is untitled
            if doc_name starts with "Untitled" then
                -- Get document content to analyze for title
                set doc_text to text of current_doc
                
                -- Try to extract a meaningful title from first line
                set first_line to ""
                if length of doc_text > 0 then
                    set first_line to paragraph 1 of doc_text
                    -- Clean up the first line for filename use
                    set first_line to do shell script "echo " & quoted form of first_line & " | sed 's/[^a-zA-Z0-9 ]//g' | sed 's/^ *//g' | sed 's/ *$//g' | tr ' ' '_' | cut -c1-50"
                end if
                
                -- Generate filename
                set timestamp to do shell script "date '+%Y%m%d_%H%M%S'"
                if length of first_line > 3 and first_line ≠ "" then
                    set filename to first_line & "_" & timestamp & ".txt"
                else
                    set filename to "TextEdit_" & timestamp & "_" & doc_count & ".txt"
                end if
                
                set save_path to "/Users/thomasmulhern/unprocessed_textedits/" & filename
                
                -- Save the document
                save current_doc in POSIX file save_path
                log "Saved: " & filename
            end if
            
            -- Close this document immediately after processing
            close current_doc
            
        on error error_message
            log "Error processing document: " & error_message
            -- Try to close the document even if there was an error
            try
                close document 1
            end try
        end try
    end repeat
    
    log "All documents processed and closed"
end tell
EOF

echo "Script completed. Check /Users/thomasmulhern/unprocessed_textedits/ for saved files."