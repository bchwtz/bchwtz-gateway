package tools

import (
	filename "github.com/keepeye/logrus-filename"
	"github.com/sirupsen/logrus"
)

func SetupLogs() {
	customFormatter := &logrus.TextFormatter{}
	customFormatter.TimestampFormat = "2006-01-02 15:04:05"
	customFormatter.FullTimestamp = true
	logrus.SetFormatter(customFormatter)
	logrus.SetLevel(logrus.DebugLevel)
	filenameHook := filename.NewHook()
	filenameHook.Field = "line"
	logrus.AddHook(filenameHook)
}
