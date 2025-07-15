import React, { useState } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import WorkflowPreview from './WorkflowPreview';

interface WorkflowStep {
  id: string;
  name: string;
  displayName?: string;
}

interface WorkflowStepsProps {
  steps: WorkflowStep[];
  onReorder: (newOrder: string[]) => void;
  onGenerate?: () => void;
}

interface SortableItemProps {
  step: WorkflowStep;
}

const SortableItem: React.FC<SortableItemProps> = ({ step }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: step.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className={`bg-white p-4 rounded-md border shadow-sm mb-2 cursor-move
        ${isDragging ? 'opacity-50 border-blue-400 z-50' : 'border-gray-200'}
        hover:border-blue-400 transition-colors`}
    >
      <div className="flex items-center space-x-3">
        <span className="text-gray-400">⋮⋮</span>
        <span className="text-sm text-gray-700">{step.displayName || step.name}</span>
      </div>
    </div>
  );
};

const WorkflowSteps: React.FC<WorkflowStepsProps> = ({ steps, onReorder, onGenerate }) => {
  const [localSteps, setLocalSteps] = useState(steps);
  const [showPreview, setShowPreview] = useState(true);

  // Sync local steps with parent's steps when they change
  React.useEffect(() => {
    setLocalSteps(steps);
  }, [steps]);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    
    if (over && active.id !== over.id) {
      setLocalSteps((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id);
        const newIndex = items.findIndex((item) => item.id === over.id);
        
        const newItems = arrayMove(items, oldIndex, newIndex);
        onReorder(newItems.map(item => item.id));
        return newItems;
      });
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-medium text-gray-700">Drag to reorder steps:</h4>
        <button
          onClick={() => setShowPreview(!showPreview)}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          {showPreview ? 'Hide' : 'Show'} Preview
        </button>
      </div>
      
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext
          items={localSteps}
          strategy={verticalListSortingStrategy}
        >
          <div className="space-y-2">
            {localSteps.map((step) => (
              <SortableItem key={step.id} step={step} />
            ))}
          </div>
        </SortableContext>
      </DndContext>
      
      {showPreview && (
        <WorkflowPreview steps={localSteps} />
      )}
      
      {onGenerate && (
        <button
          onClick={onGenerate}
          className="mt-4 w-full py-2 px-4 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
        >
          ✨ Generate New Workflow
        </button>
      )}
    </div>
  );
};

export default WorkflowSteps; 