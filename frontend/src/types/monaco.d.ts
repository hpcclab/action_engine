declare module '@monaco-editor/react' {
  import { ComponentType } from 'react';

  interface EditorProps {
    height?: string | number;
    width?: string | number;
    language?: string;
    theme?: string;
    value?: string;
    defaultValue?: string;
    defaultLanguage?: string;
    defaultPath?: string;
    path?: string;
    options?: any;
    onChange?: (value: string | undefined, event: any) => void;
    onMount?: (editor: any, monaco: any) => void;
    beforeMount?: (monaco: any) => void;
    onValidate?: (markers: any[]) => void;
    loading?: React.ReactNode;
    className?: string;
  }

  const Editor: ComponentType<EditorProps>;
  export default Editor;
} 