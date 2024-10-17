import MDEditor from '@uiw/react-md-editor';
import '../styles/components/MarkdownEditor.css';
import { useState } from 'react';

const MarkdownEditor = () => {
  const [value, setValue] = useState('**Hello world!**');

  return (
    <div className="container">
      <MDEditor value={value} onChange={setValue} />
      <MDEditor.Markdown source={value} />
    </div>
  );
};

export default MarkdownEditor;
