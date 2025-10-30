/**
 * Utility functions
 */

export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('en-US').format(num);
};

export const formatDate = (date: string | Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date));
};

export const getAvatarUrl = (userId: string, avatar: string | null): string => {
  if (avatar) {
    return `https://cdn.discordapp.com/avatars/${userId}/${avatar}.png`;
  }
  return `https://cdn.discordapp.com/embed/avatars/${parseInt(userId) % 5}.png`;
};

export const getServerIconUrl = (guildId: string, icon: string | null): string | null => {
  if (icon) {
    return `https://cdn.discordapp.com/icons/${guildId}/${icon}.png`;
  }
  return null;
};

export const calculateLevelXP = (level: number): number => {
  return 5 * (level ** 2) + 50 * level + 100;
};

export const calculateXPProgress = (xp: number, level: number): number => {
  const currentLevelXP = calculateLevelXP(level);
  const nextLevelXP = calculateLevelXP(level + 1);
  const progress = ((xp - currentLevelXP) / (nextLevelXP - currentLevelXP)) * 100;
  return Math.max(0, Math.min(100, progress));
};
