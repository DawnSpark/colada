
export function formatDate(date: Date): string {
    return (date).toISOString().slice(0, 19).replace(/-/g, "/").replace("T", " ");

}