import { toast } from "sonner";

export const showSuccess = (message: string, action?: { label: string, onClick: () => void }) => {
  toast.success(message, {
    action: action ? {
      label: action.label,
      onClick: action.onClick,
    } : undefined,
  });
};

export const showError = (message: string) => {
  toast.error(message);
};

export const showLoading = (message: string) => {
  return toast.loading(message);
};

export const dismissToast = (toastId: string) => {
  toast.dismiss(toastId);
};
