#!/bin/bash

# Simple script to close all untitled TextEdit documents
osascript -e '
tell application "TextEdit"
    repeat
        set doc_count to count of documents
        if doc_count = 0 then exit repeat
        
        try
            set current_doc to document 1
            set doc_name to name of current_doc
            
            if doc_name starts with "Untitled" then
                close current_doc
                log "Closed: " & doc_name
            else
                exit repeat
            end if
        on error
            try
                close document 1
            end try
        end try
    end repeat
    
    log "All untitled documents closed"
end tell
'