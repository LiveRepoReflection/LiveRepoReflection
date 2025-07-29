public class ContentRequest {
    private final int userLocation;
    private final String contentId;

    public ContentRequest(int userLocation, String contentId) {
        this.userLocation = userLocation;
        this.contentId = contentId;
    }

    public int getUserLocation() {
        return userLocation;
    }

    public String getContentId() {
        return contentId;
    }
}