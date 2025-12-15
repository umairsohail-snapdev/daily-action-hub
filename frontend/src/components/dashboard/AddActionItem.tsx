import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { PlusCircle, Loader2 } from "lucide-react";

interface AddActionItemProps {
  onAddItem: (description: string) => Promise<void> | void;
  placeholderText: string;
}

export function AddActionItem({ onAddItem, placeholderText }: AddActionItemProps) {
  const [description, setDescription] = useState("");
  const [isAdding, setIsAdding] = useState(false);

  const handleAdd = async () => {
    if (description.trim()) {
      setIsAdding(true);
      try {
        await onAddItem(description.trim());
        setDescription("");
      } finally {
        setIsAdding(false);
      }
    }
  };

  return (
    <div className="flex items-center gap-2 mt-4 p-2 bg-muted/50 rounded-lg">
      <Input
        type="text"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder={placeholderText}
        className="flex-grow bg-background"
        onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
        disabled={isAdding}
      />
      <Button onClick={handleAdd} size="sm" disabled={isAdding}>
        {isAdding ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <PlusCircle className="h-4 w-4 mr-2" />}
        Add
      </Button>
    </div>
  );
}