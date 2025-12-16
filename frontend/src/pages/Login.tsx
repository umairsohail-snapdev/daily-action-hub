import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Calendar } from "lucide-react";
import { showSuccess, showError } from "@/utils/toast";
import { api } from "@/lib/api";

const Login = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const API_BASE_URL = "http://localhost:8000";

  useEffect(() => {
    // Handle URL parameters (backend code flow - future proofing)
    const tokenParam = searchParams.get("token");
    
    // Handle Hash Fragment (Google Implicit Flow)
    const hash = window.location.hash;
    let accessToken = null;

    if (hash) {
      const params = new URLSearchParams(hash.substring(1)); // remove the '#'
      accessToken = params.get("access_token");
      const errorParam = params.get("error");
      
      if (errorParam) {
        showError(`Google Login Error: ${errorParam}`);
        return;
      }
    }

    const token = tokenParam || accessToken;
    const error = searchParams.get("error");
    const details = searchParams.get("details");

    if (token) {
      // If we have an accessToken from the hash, it's a Google Access Token.
      // We need to exchange it for an App JWT.
      if (accessToken) {
          console.log("Verifying Google Token...");
          const verifyGoogle = async () => {
              try {
                  const data = await api.googleLogin(accessToken);
                  console.log("Google Login Success, received JWT:", data.access_token);
                  
                  // Store the APP JWT for backend authentication
                  localStorage.setItem("jwt_token", data.access_token);
                  
                  // Store the Google Access Token separately for Google API calls (like Calendar)
                  localStorage.setItem("google_access_token", accessToken);
                  
                  showSuccess("Successfully logged in!");
                  navigate("/");
              } catch (err) {
                  console.error("Google Verification Failed:", err);
                  showError("Failed to verify Google token");
              }
          }
          verifyGoogle();
      } else if (tokenParam) {
           // Direct token from backend (if we used that flow)
           localStorage.setItem("jwt_token", tokenParam);
           showSuccess("Successfully logged in!");
           navigate("/");
      }
    }

    if (error) {
        showError(`Login Failed: ${details || "Unknown error"}`);
    }
  }, [searchParams, navigate]);

  const handleGoogleLogin = () => {
    window.location.href = `${API_BASE_URL}/auth/login`;
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50/50">
      <Card className="w-[400px] shadow-lg border-0">
        <CardHeader className="text-center space-y-2 pb-6">
          <div className="flex justify-center mb-4">
            <div className="bg-primary/10 p-3 rounded-full">
              <Calendar className="w-8 h-8 text-primary" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold">Daily Action Hub</CardTitle>
          <CardDescription className="text-base">
            Turn your meetings into action items automatically.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button
            onClick={handleGoogleLogin}
            className="w-full h-12 text-base font-medium flex gap-3 items-center justify-center"
            disabled={isLoading}
          >
            <svg viewBox="0 0 24 24" className="h-5 w-5" aria-hidden="true"><path d="M12.0003 20.45c4.6593 0 8.364-3.5346 8.364-7.8596 0-0.638-.0697-1.251-.195-1.8406H12.0003v3.481h4.6936C16.4862 15.342 14.4758 16.8906 12.0003 16.8906c-2.8596 0-5.2766-2.122-5.992-4.9666l-3.666 2.781C3.805 17.606 7.5913 20.45 12.0003 20.45z" fill="#34A853"></path><path d="M12.0003 7.1094c2.2536 0 4.1627 1.0256 5.378 2.5936l2.6036-2.553C18.2323 5.3096 15.3996 3.55 12.0003 3.55 7.5913 3.55 3.805 6.394 2.3423 10.294l3.666 2.781C6.7237 10.1846 9.1407 8.0626 12.0003 7.1094z" fill="#EA4335"></path><path d="M6.0083 13.075c-.1796-.583-.2846-1.199-.2846-1.84 0-0.641.105-1.257.2846-1.84l-3.666-2.781C1.637 8.4456 1.156 10.25 1.156 12.195c0 1.945.481 3.7494 1.3253 5.561l3.666-2.781c-.3587-1.125-.561-2.316-.561-3.54z" fill="#FBBC05"></path><path d="M2.3423 10.294L6.0083 13.075c.7154-2.8446 3.1324-4.9666 5.992-4.9666 2.2536 0 4.1627 1.0256 5.378 2.5936l2.6036-2.553C18.2323 5.3096 15.3996 3.55 12.0003 3.55 7.5913 3.55 3.805 6.394 2.3423 10.294z" fill="#4285F4"></path></svg>
            Continue with Google
          </Button>
        </CardContent>
        <CardFooter className="flex justify-center pb-6">
            <p className="text-xs text-center text-muted-foreground">
                By clicking continue, you agree to our <a href="#" className="underline">Terms of Service</a> and <a href="#" className="underline">Privacy Policy</a>.
            </p>
        </CardFooter>
      </Card>
    </div>
  );
};

export default Login;