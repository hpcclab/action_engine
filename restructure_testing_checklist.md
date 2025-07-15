# Workflow Restructuring Feature - Testing Checklist

## Functional Tests

### Basic Functionality
- [ ] Can enter restructuring mode by clicking "Restructure Workflow"
- [ ] Can exit restructuring mode by clicking "Cancel Restructuring"
- [ ] Drag and drop works smoothly between all steps
- [ ] Visual feedback shows when reordering is successful
- [ ] Error messages display when reordering fails

### Order Persistence
- [ ] Reordered steps maintain their new order during the session
- [ ] Reset button restores the original order
- [ ] Multiple reorderings work without issues

### Workflow Generation
- [ ] "Generate New Workflow" creates a new workflow with the reordered steps
- [ ] The new workflow executes with the correct order
- [ ] The new workflow appears in the workflow history

## Edge Cases to Test

### Error Scenarios
- [ ] Network failure during reordering
- [ ] Invalid step combinations (if any business logic constraints exist)
- [ ] Rapid consecutive reorderings
- [ ] Reordering while a workflow is executing

### Different Workflow Types
- [ ] Workflows with 2 steps
- [ ] Workflows with 3-4 steps (current case)
- [ ] Workflows with 5+ steps
- [ ] Workflows with conditional branches (if supported)

## Performance Tests
- [ ] Reordering responds quickly (< 1 second)
- [ ] UI remains responsive during backend calls
- [ ] No memory leaks after multiple reorderings

## User Experience
- [ ] Clear visual indicators for draggable items
- [ ] Smooth drag animations
- [ ] Clear success/error messages
- [ ] Intuitive button labels and placement

## Integration Tests
- [ ] New workflows appear in workflow history
- [ ] Execution status updates correctly for restructured workflows
- [ ] API endpoints handle concurrent requests properly 