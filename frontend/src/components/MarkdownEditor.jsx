// src/MarkdownEditor.js
import React from 'react';
import { marked } from 'marked';
import '../styles/components/MarkdownEditor.css';

const MarkdownEditor = ({ markdown, setMarkdown }) => {
  const handleChange = (event) => {
    setMarkdown(event.target.value);
  };

  const getMarkdownText = () => {
    return { __html: marked(markdown) };
  };

  return (
    <div className="markdown-editor">
      <textarea
        id="markdown-textarea"
        value={markdown}
        onChange={handleChange}
        rows={10}
        style={{ width: '100%', fontSize: '16px' }}
        placeholder="Type something here..."
      />
      <div
        className="markdown-preview"
        dangerouslySetInnerHTML={getMarkdownText()}
      />
    </div>
  );
};

export default MarkdownEditor;
