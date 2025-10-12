import {isAxiosError} from "axios";
import {toast} from "sonner";

export class ErrorUtils {
  
  public static getErrorMessage(error: Error): string | null {
    if (isAxiosError(error) && error.response && error.response.data) {
      return error.response.data.detail;
    }
    return error.message;
  }
  
  public static displayAxiosError(error: Error, defaultMessage?: string): void {
    if (isAxiosError(error)) {
      toast.error(ErrorUtils.getErrorMessage(error) ?? defaultMessage)
    }
    console.error(error);
  }
}