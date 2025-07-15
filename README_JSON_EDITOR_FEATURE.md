# Workflow JSON Editor Feature

## Overview

The Workflow JSON Editor is a new feature that allows users to view and directly edit workflow JSON definitions in addition to the existing visual drag-and-drop interface. This provides advanced users with fine-grained control over workflow structure while maintaining the user-friendly GUI for most operations.

## Features

### 1. **Dual Interface**
- **Visual Editor**: Drag-and-drop interface for easy workflow restructuring
- **JSON Editor**: Code editor with syntax highlighting for direct JSON manipulation

### 2. **Monaco Editor Integration**
- Full-featured code editor with syntax highlighting
- JSON validation and error checking
- Auto-formatting and intelligent editing features
- Dark theme for comfortable editing

### 3. **Tabbed Sections**
- **Full JSON**: Complete workflow definition
- **States Only**: Edit just the workflow states
- **Metadata**: Edit workflow metadata (StartAt, Comment, etc.)

### 4. **Validation & Safety**
- Real-time JSON syntax validation
- AWS Step Functions structure validation
- State reference validation (Next, StartAt)
- Prevents saving invalid workflows

### 5. **Save & Regenerate**
- Direct workflow updates
- Automatic AWS Step Functions state machine updates
- New execution creation after successful saves

## How to Use

### Accessing the JSON Editor

1. **Generate or load a workflow** using the main interface
2. In the **Execution Result** section, you'll see two tabs:
   - 📊 **Visual Editor** (existing drag-and-drop interface)
   - 📝 **JSON Editor** (new code editor)
3. Click on the **JSON Editor** tab

### Using the JSON Editor

#### Basic Operations

1. **View Workflow JSON**: The editor loads the current workflow definition automatically
2. **Edit the JSON**: Use the Monaco editor to modify the workflow structure
3. **Validate**: Click "Validate" to check for syntax and structure errors
4. **Save**: Click "Save & Regenerate" to apply changes and create a new execution

#### Tab Navigation

- **Full JSON**: Edit the complete workflow definition
- **States Only**: Focus on just the workflow states for easier editing
- **Metadata**: Edit workflow-level properties like StartAt, Comment, etc.

#### Status Indicators

- **🟡 Unsaved changes**: Shows when you have modifications that haven't been saved
- **✅ Saved**: Indicates the current content matches the saved version
- **❌ Validation Error**: Displays specific validation errors with helpful messages

### Example Workflow JSON Structure

```json
{
  "Comment": "Music recommendation workflow",
  "StartAt": "t1",
  "States": {
    "t1": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-2:559198857332:function:username2id",
      "Next": "t2"
    },
    "t2": {
      "Type": "Task", 
      "Resource": "arn:aws:lambda:us-east-2:559198857332:function:getusermood",
      "Next": "t3"
    },
    "t3": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-2:559198857332:function:recommendsong", 
      "Next": "t4"
    },
    "t4": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-2:559198857332:function:playmusic",
      "End": true
    }
  }
}
```

## Backend API Endpoints

### New Endpoints

#### `POST /workflows/{workflow_name}/update`

Updates a workflow's JSON definition and regenerates it.

**Request Body:**
```json
{
  "definition": {
    "StartAt": "t1",
    "States": { ... }
  }
}
```

**Response:**
```json
{
  "message": "Workflow updated and executed successfully",
  "execution_arn": "arn:aws:states:...",
  "state_machine_arn": "arn:aws:states:...",
  "updated_existing": true
}
```

#### Enhanced `GET /workflows/{workflow_name}`

Returns workflow definition including the full JSON structure.

**Response:**
```json
{
  "workflow_name": "workflow_name",
  "definition": { ... },
  "steps": [ ... ]
}
```

## Technical Implementation

### Frontend Components

#### `WorkflowJsonEditor.tsx`
- Main JSON editor component using Monaco Editor
- Handles validation, saving, and tab navigation
- Integrates with existing workflow context

#### Updated `ExecutionResult.tsx`
- Added tab navigation between Visual and JSON editors
- Integrated JSON editor with existing workflow display
- Added message handling for editor feedback

### Backend Features

#### Validation System
- JSON syntax validation
- AWS Step Functions structure validation
- State reference integrity checks
- Comprehensive error messages

#### State Machine Management
- Updates existing state machines when possible
- Creates new versioned state machines as fallback
- Maintains workflow registry consistency

## Error Handling

### Validation Errors
- **JSON Syntax**: Clear messages for syntax issues
- **Missing Fields**: Identifies required fields (StartAt, States)
- **Invalid References**: Catches broken state transitions
- **Structure Issues**: Validates AWS Step Functions format

### Save Errors
- **Network Issues**: Handles API communication failures
- **AWS Errors**: Reports Step Functions update failures
- **Permission Issues**: Clear messages for access problems

## Benefits

### For Power Users
- **Direct Control**: Fine-tune workflow definitions without GUI limitations
- **Bulk Edits**: Make large-scale changes efficiently
- **Advanced Features**: Access AWS Step Functions features not in GUI
- **Copy/Paste**: Easy workflow sharing and templating

### For All Users
- **Transparency**: See exactly how workflows are structured
- **Learning**: Understand AWS Step Functions format
- **Backup**: Easy way to export/import workflow definitions
- **Debugging**: Examine workflow structure when issues occur

## Best Practices

### When to Use JSON Editor
- Fine-tuning state properties
- Adding advanced AWS Step Functions features
- Bulk renaming or restructuring
- Copying workflow patterns
- Debugging complex workflows

### When to Use Visual Editor
- Initial workflow creation
- Simple reordering of steps
- Learning workflow concepts
- Quick structural changes

### Safety Tips
- Always validate before saving
- Use "Reset" if you make mistakes
- Keep backups of working workflows
- Test changes in development first

## Future Enhancements

### Planned Features
- **Schema Validation**: Full AWS Step Functions schema validation
- **Auto-completion**: Intelligent code completion for state properties
- **Diff View**: Visual comparison of changes
- **Import/Export**: Dedicated workflow import/export functionality
- **Templates**: Pre-built workflow templates
- **Collaboration**: Multi-user editing features

### Performance Optimizations
- **Lazy Loading**: Load large workflows efficiently
- **Virtualization**: Handle very large JSON files
- **Caching**: Improve editor responsiveness
- **Real-time Sync**: Keep visual and JSON views synchronized

## Troubleshooting

### Common Issues

#### "Monaco Editor not loading"
- Ensure `@monaco-editor/react` is installed
- Check network connectivity for CDN resources
- Verify browser compatibility

#### "Validation errors after saving"
- Check JSON syntax carefully
- Ensure all state references are valid
- Verify required fields are present

#### "Cannot save workflow"
- Check network connection to backend
- Verify AWS permissions
- Ensure workflow name is valid

#### "Changes not reflecting in visual editor"
- Refresh the page after saving
- Check for JavaScript console errors
- Verify the workflow was saved successfully

## Conclusion

The Workflow JSON Editor feature provides a powerful complement to the existing visual interface, enabling both novice and expert users to work with workflows in their preferred mode. The combination of intuitive GUI operations and direct code editing offers the best of both worlds for workflow management. 