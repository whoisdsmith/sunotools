import { useSignOut } from "../../../hooks/auth";
import { FiLogOut } from "react-icons/fi";

export const SignOutButton = () => {
  const { signOut } = useSignOut();

  return (
    <button
      onClick={signOut}
      type="button"
      className="btn btn-ghost w-full"
    >
      <FiLogOut className="h-5 w-5 mr-2" />
      Sign Out
    </button>
  );
};
