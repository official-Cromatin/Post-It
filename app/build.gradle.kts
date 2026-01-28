// Contents of this file have been copied as explained on the setup guide (https://jda.wiki/setup/intellij/) by jda

plugins {
    application
    id("com.gradleup.shadow") version "8.3.1"
}

group = "org.postit"
version = "1.0"

val jdaVersion = "6.3.0"

repositories {
    mavenCentral()
}

dependencies {
    implementation("net.dv8tion:JDA:$jdaVersion")

    // Use JUnit Jupiter for testing.
    testImplementation(libs.junit.jupiter)

    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

application {
    mainClass = "postit.App"
}

tasks.withType<JavaCompile> {
    options.encoding = "UTF-8"
    options.isIncremental = true

    // Set this to the version of java you want to use,
    // the minimum required for JDA is 1.8
    sourceCompatibility = "1.8"
}
