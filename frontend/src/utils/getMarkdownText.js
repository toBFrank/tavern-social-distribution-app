import { marked } from 'marked';

export const getMarkdownText = (markdown) => {
  return { __html: marked(markdown) };
};
