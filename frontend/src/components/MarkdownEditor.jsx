import React from 'react';
import { getMarkdownText } from '../utils/getMarkdownText';
import '../styles/components/MarkdownEditor.css';

const MarkdownEditor = ({ markdown, setMarkdown }) => {
  const handleChange = (event) => {
    setMarkdown(event.target.value);
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
        dangerouslySetInnerHTML={getMarkdownText(markdown)}
      />
    </div>
  );
};

export default MarkdownEditor;
