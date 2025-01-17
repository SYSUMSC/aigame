import { ref } from 'vue';
import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null);

  const setUser = (newUser: User | null) => {
    user.value = newUser;
  };

  const isLoggedIn = () => {
    return user.value !== null;
  };

  return { user, setUser, isLoggedIn };
}, {
  persist: true
});

interface User {
  id: number;
  username: string;
  email: string;
  name: string;
  student_id: string;
  is_active: boolean;
  team_id: number | null;
  token: string;
}
